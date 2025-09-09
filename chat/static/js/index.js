document.addEventListener("DOMContentLoaded", () => {
  const chat = document.querySelector('#chat');
  const input = document.querySelector('#input');
  const botaoEnviar = document.querySelector('#botao-enviar');

  if (!chat || !input || !botaoEnviar) {
    console.error("Elementos #chat, #input ou #botao-enviar não encontrados.");
    return;
  }

  async function enviarMensagem() {
    if (!input.value) return;
    const mensagem = input.value;
    input.value = "";

    const novaBolha = criaBolhaUsuario();
    novaBolha.textContent = mensagem;
    chat.appendChild(novaBolha);

    const novaBolhaBot = criaBolhaBot();
    chat.appendChild(novaBolhaBot);
    vaiParaFinalDoChat();
    novaBolhaBot.textContent = "Buscando sua resposta ...";

    // Timeout opcional para evitar ficar pendurado
    const ctrl = new AbortController();
    const to = setTimeout(() => ctrl.abort(), 30000); // 30s
    try {
      const resp = await fetch("/api/chat/rag", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ msg: mensagem }), // opcional: {category: "ppc"}
        signal: ctrl.signal
      });

      if (!resp.ok) {
        const txt = await resp.text().catch(() => "");
        console.error("Erro HTTP:", resp.status, txt);
        throw new Error(`HTTP ${resp.status}`);
      }

      const data = await resp.json(); // parse JSON
      const answer = (data && data.answer) ? data.answer : "Não foi possível obter a resposta.";
      const fontes = Array.isArray(data?.sources) ? data.sources : [];

      novaBolhaBot.innerHTML = answer.replace(/\n/g, "<br>");
      if (fontes.length) {
        novaBolhaBot.innerHTML += "<br><br><b>Fontes:</b><br>" + fontes.map(s => `- ${s}`).join("<br>");
      }
    } catch (err) {
      console.error("Falha no fetch:", err);
      if (err.name === "AbortError") {
        novaBolhaBot.textContent = "Tempo de resposta excedido. Tente novamente.";
      } else {
        novaBolhaBot.textContent = "Erro ao consultar a API. Verifique o console.";
      }
    } finally {
      clearTimeout(to);
      vaiParaFinalDoChat();
    }
  }

  function criaBolhaUsuario() {
    const bolha = document.createElement('p');
    bolha.className = 'chat__bolha chat__bolha--usuario';
    return bolha;
  }
  function criaBolhaBot() {
    const bolha = document.createElement('p');
    bolha.className = 'chat__bolha chat__bolha--bot';
    return bolha;
  }
  function vaiParaFinalDoChat() { chat.scrollTop = chat.scrollHeight; }

  botaoEnviar.addEventListener('click', enviarMensagem);
  input.addEventListener("keyup", e => { if (e.key === "Enter") botaoEnviar.click(); });
});
