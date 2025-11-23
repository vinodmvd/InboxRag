const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatStream = document.getElementById('chat-stream');


function appendMessage(sender, text) {
    if (chatBox.classList.contains('empty')) {
        chatBox.innerHTML = '';
        chatBox.classList.remove('empty');
    }
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ' + sender;
    msgDiv.textContent = text;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}


userInput.addEventListener('keydown', function (event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        chatForm.requestSubmit();
    }
});


function onStreamChunk(chunkHtml) {
    document.getElementById("chat-stream").insertAdjacentHTML("beforeend", `<li>${chunkHtml}</li>`);
}


chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const message = userInput.value.trim();
    if (!message) return;

    appendMessage("user", message);
    userInput.value = "";

    const botMsgDiv = document.createElement("div");
    botMsgDiv.className = "message bot";
    chatBox.appendChild(botMsgDiv);

    //Placeholder
    botMsgDiv.textContent = "Thinking…";

    const rawBuffer = document.createElement("div");
    rawBuffer.style.display = "none";

    const pretty = document.createElement("div");

    let fullResponse = "";
    let gotFirstChunk = false;

    const response = await fetch("/get", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    const renderMarkdown = () => {
        pretty.innerHTML = marked.parse(fullResponse);
        pretty.querySelectorAll("pre code").forEach((block) => hljs.highlightElement(block));
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        if (!gotFirstChunk) {
            botMsgDiv.textContent = "";
            botMsgDiv.appendChild(rawBuffer);
            botMsgDiv.appendChild(pretty);
            gotFirstChunk = true;
        }

        const chunk = decoder.decode(value);

        fullResponse += chunk;
        rawBuffer.textContent = fullResponse;

        renderMarkdown();
    }

    renderMarkdown();
});