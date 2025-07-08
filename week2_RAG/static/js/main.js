document.addEventListener("DOMContentLoaded", () => {
    console.log("JavaScript loaded successfully!");

    const questionInput = document.getElementById("question");
    const submitButton = document.getElementById("submit-btn");
    const resultSection = document.getElementById("result-section");

    console.log("DOM elements initialized.");

    submitButton.addEventListener("click", async () => {
        const question = questionInput.value.trim();
        console.log("Submit button clicked.");
        console.log("Question input:", question);

        if (!question) {
            alert("请输入问题！");
            console.log("No question provided.");
            return;
        }

        try {
            console.log("Sending request to /ask endpoint...");
            const response = await fetch("/ask", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ question }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            console.log("Response received:", response);
            const data = await response.json();
            console.log("Parsed response data:", data);

            const answer = data.answer.result; // 解析后端返回的 result 字段
            console.log("Answer extracted:", answer);

            const card = document.createElement("div");
            card.className = "result-card";
            card.innerHTML = `<p>${answer}</p>`;
            resultSection.appendChild(card);
            console.log("Answer card added to result section.");
        } catch (error) {
            console.error("Error fetching answer:", error);
            alert("获取答案时出错，请稍后重试。");
        }
    });
});
