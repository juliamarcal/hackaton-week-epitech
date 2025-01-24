const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");

let userMessage = null; // Variable to store user's message
const inputInitHeight = chatInput.scrollHeight;

const createChatLi = (message, className) => {
    // Create a chat <li> element with passed message and className
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", `${className}`);
    let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi; // return chat <li> element
}

const createDocumentElement = (documentName, documentHref) => {
    const documentsContainer = document.createElement("div");
    documentsContainer.classList.add("documents");

    const documentElement = document.createElement("div");
    documentElement.classList.add("document-element");
    documentElement.innerHTML = `
        <img src="static/icons/icone_fichier.png" class="icon-response" />
        <a href="${documentHref || '#'}">${documentName || 'Document Name'}</a>
    `;
    documentsContainer.appendChild(documentElement);

    return documentsContainer;
}


const generateResponse = async (chatElement) => {
    const messageElement = chatElement.querySelector("p");
    var keyWords;
    var filePath;
    var analysis;

    try {
        const firstPromptReponse = await fetch('http://localhost:3000/send-question-gpt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "message": "Extract the keywords from this text: [" + userMessage + "] and then answer me with the 5 (or less if it has less than 5 words) most important keywords, separated by a comma. The answer should be in the following format: keyword1 (optional), keyword2 (optional), keyword3 (optional), keyword4 (optional), keyword5 (optional)"
            }),
        });

        if (!firstPromptReponse.ok) {
            throw new Error('Network response was not ok: ' + firstPromptReponse.statusText);
        }

        const promptResponseJson = await firstPromptReponse.json();
        keyWords = promptResponseJson['answer'];
        keyWords = keyWords.replace(/\s+/g, ' ').replace(/keyword/gi, ''); 
        keyWords = keyWords.lower()  

    } catch (error) {
        console.log("Não obteve KEY WORDS properly");
    } finally {
        chatbox.scrollTo(0, chatbox.scrollHeight);
    }

    try {
        const keyWordsResponse = await fetch('http://127.0.0.1:5000/process-keywords', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "keywords": keyWords
            }),
        });

        if (!keyWordsResponse.ok) {
            throw new Error('Network response was not ok: ' + keyWordsResponse.statusText);
        }

        filePath = await keyWordsResponse.json();
    } catch (error) {
        messageElement.classList.add("error");
        messageElement.textContent = "Oops! Something went wrong. Please try again.";
        console.log("não funcionou");
    } finally {
        chatbox.scrollTo(0, chatbox.scrollHeight);

        if (filePath == null) {
            fetch('http://localhost:3000/send-question-gpt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "message": userMessage
                }),
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok: ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log(data['answer']);
                    messageElement.textContent = data['answer'].trim();
                })
                .catch(() => {
                    messageElement.classList.add("error");
                    messageElement.textContent = "Oops! Something went wrong. Please try again.";
                    console.log("não funcionou");
                }).finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));

                return null

        } else {
            try {
                const fileAnalysisResponse = await fetch('http://127.0.0.1:5000/extract-answer-from-file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        "filePath" : filePath, 
                        "question" : userMessage
                    }),
                })
        
                if (fileAnalysisResponse.ok) {
                    const analysisResponse = await fileAnalysisResponse.json();
                    messageElement.textContent = analysisResponse['answer'];
                    filePathSplited = filePath.split('/');

                    return { name: filePathSplited[filePathSplited.length - 1], link: "http://127.0.0.1:8080/"+filePath }
                 } else {
                    throw new Error('Network response was not ok: ' + fileAnalysisResponse.statusText);
                 }
            } catch (error) {
                console.log("Não obteve ANALYSIS properly");
                messageElement.classList.add("error");
                messageElement.textContent = "Oops! Something went wrong. Please try again.";
            } finally {
                chatbox.scrollTo(0, chatbox.scrollHeight);
            }
        }
    }
}

const handleChat =  () => {
    userMessage = chatInput.value.trim(); // Get user entered message and remove extra whitespace
    if (!userMessage) return;

    // Clear the input textarea and set its height to default
    chatInput.value = "";
    chatInput.style.height = `${inputInitHeight}px`;

    // Append the user's message to the chatbox
    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight);

    setTimeout(async () => {
        // Display "Thinking..." message while waiting for the response
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        documentInfo = await generateResponse(incomingChatLi);

        console.log(documentInfo.name, documentInfo.link);

        if(documentInfo != null){
            const newDocumentsContainer = createDocumentElement(documentInfo.name, documentInfo.link);
            chatbox.appendChild(newDocumentsContainer);
        }
    }, 600);
}

chatInput.addEventListener("input", () => {
    // Adjust the height of the input textarea based on its content
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    // If Enter key is pressed without Shift key and the window 
    // width is greater than 800px, handle the chat
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
});

sendChatBtn.addEventListener("click", handleChat);
// closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
// chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));