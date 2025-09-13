document.addEventListener("DOMContentLoaded", () => {
  const chat = document.querySelector('#chat');
  const input = document.querySelector('#input');
  const botaoEnviar = document.querySelector('#botao-enviar');

  if (!chat || !input || !botaoEnviar) {
    console.error("Elementos #chat, #input ou #botao-enviar não encontrados.");
    return;
  }

  // Função para escapar HTML perigoso
  function escapeHTML(str) {
    return str.replace(/[&<>"']/g, m =>
      ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#039;" }[m])
    );
  }

  // Função para rolagem suave
  function vaiParaFinalDoChat() {
    chat.scrollTo({ top: chat.scrollHeight, behavior: "smooth" });
  }

  // Criação das bolhas
  function criaBolhaUsuario(msg) {
    const bolha = document.createElement('p');
    bolha.className = 'chat__bolha chat__bolha--usuario';
    bolha.textContent = msg;
    return bolha;
  }

  function criaBolhaBot(conteudo = "") {
    const bolha = document.createElement('p');
    bolha.className = 'chat__bolha chat__bolha--bot';
    bolha.textContent = conteudo;
    return bolha;
  }

  // Animação de "digitando..."
  function animaLoading(element) {
    let dots = 0;
    const interval = setInterval(() => {
      dots = (dots + 1) % 4;
      element.textContent = "Buscando sua resposta" + ".".repeat(dots);
    }, 500);
    return interval;
  }

  async function enviarMensagem() {
    if (!input.value.trim()) return;

    const mensagem = input.value.trim();
    input.value = "";

    // Adiciona bolha do usuário
    const novaBolhaUsuario = criaBolhaUsuario(mensagem);
    chat.appendChild(novaBolhaUsuario);

    // Adiciona bolha do bot com loading
    const novaBolhaBot = criaBolhaBot();
    chat.appendChild(novaBolhaBot);
    vaiParaFinalDoChat();

    const loading = animaLoading(novaBolhaBot);

    // Timeout opcional para evitar ficar pendurado
    const ctrl = new AbortController();
    const to = setTimeout(() => ctrl.abort(), 30000); // 30s

    try {
      const resp = await fetch("/api/chat/rag", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_query: mensagem }),
        signal: ctrl.signal
      });

      if (!resp.ok) {
        const txt = await resp.text().catch(() => "");
        console.error("Erro HTTP:", resp.status, txt);
        throw new Error(`HTTP ${resp.status}`);
      }

      const data = await resp.json();
      const answer = data?.answer || "Não foi possível obter a resposta.";
      const fontes = Array.isArray(data?.sources) ? data.sources : [];

      // Atualiza bolha do bot
      novaBolhaBot.innerHTML = escapeHTML(answer).replace(/\n/g, "<br>");
      if (fontes.length) {
        novaBolhaBot.innerHTML += "<br><br><b>Fontes:</b><br>" +
          fontes.map(s => `- ${escapeHTML(s)}`).join("<br>");
      }
    } catch (err) {
      console.error("Falha no fetch:", err);
      if (err.name === "AbortError") {
        novaBolhaBot.textContent = "⏳ Tempo de resposta excedido. Tente novamente.";
      } else {
        novaBolhaBot.textContent = "⚠️ Erro ao consultar a API. Verifique o console.";
      }
    } finally {
      clearInterval(loading);
      clearTimeout(to);
      vaiParaFinalDoChat();
    }
  }

  // Eventos
  botaoEnviar.addEventListener('click', enviarMensagem);

  // Enter envia, Shift+Enter quebra linha
  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      botaoEnviar.click();
    }
  });
});
