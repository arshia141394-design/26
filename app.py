from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# ============================================
# ⚠️ اینجا کلید OpenRouter رو بذار
# ============================================
API_KEY = "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"
MODEL = "meta-llama/llama-3.1-8b-instruct:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"


# ============================================================
# صفحه اصلی (ربات چت)
# ============================================================
HOME_HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 دستیار هوشمند</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Tahoma, sans-serif;
            background: linear-gradient(145deg, #0f172a 0%, #1e1b4b 100%);
            min-height: 100vh;
            display: flex; flex-direction: column;
            color: white; overflow: hidden;
        }
        .header {
            padding: 1rem; text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .header h1 { font-size: 1rem; color: #a78bfa; font-weight: normal; }

        .robot-container {
            flex: 1; display: flex; justify-content: center;
            align-items: center; flex-direction: column;
            gap: 1.5rem; transition: all 0.5s ease;
        }
        .robot-circle {
            width: 160px; height: 160px;
            background: radial-gradient(circle at 30% 30%, #2a2a2a, #000);
            border-radius: 50%; position: relative;
            box-shadow: 0 0 0 2px rgba(167,139,250,0.3),
                        0 0 40px rgba(167,139,250,0.4),
                        0 20px 60px rgba(0,0,0,0.8),
                        inset 0 -10px 30px rgba(0,0,0,0.5),
                        inset 0 10px 20px rgba(255,255,255,0.05);
            transition: all 0.4s ease;
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        .robot-circle.thinking {
            box-shadow: 0 0 0 2px rgba(56,189,248,0.5),
                        0 0 60px rgba(56,189,248,0.6),
                        0 20px 60px rgba(0,0,0,0.8);
            animation: pulse 1s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        .eyes {
            position: absolute; top: 32%; left: 50%;
            transform: translateX(-50%);
            display: flex; gap: 25px;
        }
        .eye {
            width: 18px; height: 18px;
            background: radial-gradient(circle, #a78bfa, #7c3aed);
            border-radius: 50%;
            box-shadow: 0 0 15px #a78bfa, 0 0 30px rgba(167,139,250,0.5);
            animation: blink 4s infinite;
        }
        @keyframes blink {
            0%, 90%, 100% { transform: scaleY(1); }
            95% { transform: scaleY(0.1); }
        }
        .smile {
            position: absolute; bottom: 25%; left: 50%;
            transform: translateX(-50%);
            width: 70px; height: 30px;
            border-bottom: 4px solid #a78bfa;
            border-radius: 0 0 50% 50%;
            box-shadow: 0 4px 15px rgba(167,139,250,0.6);
        }
        .smile.talking { animation: talk 0.2s infinite; }
        @keyframes talk {
            0%, 100% { height: 30px; }
            50% { height: 8px; }
        }

        .status {
            font-size: 0.85rem; color: #94a3b8;
            text-align: center; min-height: 20px;
        }
        .status.thinking { color: #38bdf8; }

        .chat-box {
            padding: 1rem; max-height: 40vh;
            overflow-y: auto; display: flex;
            flex-direction: column; gap: 0.6rem;
        }
        .msg {
            max-width: 80%; padding: 0.7rem 1rem;
            border-radius: 1rem; font-size: 0.9rem;
            line-height: 1.6; word-wrap: break-word;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .msg.user {
            align-self: flex-start;
            background: linear-gradient(135deg, #6366f1, #a855f7);
            color: white; border-bottom-left-radius: 0.3rem;
        }
        .msg.bot {
            align-self: flex-end;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(167,139,250,0.2);
            color: #e2e8f0; border-bottom-right-radius: 0.3rem;
        }
        .msg.bot::before { content: "🤖 "; margin-left: 0.3rem; }

        .input-area {
            padding: 1rem; background: rgba(0,0,0,0.3);
            border-top: 1px solid rgba(167,139,250,0.2);
            display: flex; gap: 0.5rem;
        }
        .input-area input {
            flex: 1; padding: 0.9rem 1.2rem;
            border-radius: 2rem;
            border: 1px solid rgba(167,139,250,0.3);
            background: rgba(255,255,255,0.05);
            color: white; font-family: inherit;
            font-size: 0.95rem; outline: none;
        }
        .input-area input:focus {
            border-color: #a78bfa;
            box-shadow: 0 0 20px rgba(167,139,250,0.3);
        }
        .input-area button {
            padding: 0 1.5rem; border: none;
            border-radius: 2rem;
            background: linear-gradient(135deg, #6366f1, #a855f7);
            color: white; font-family: inherit;
            font-weight: bold; font-size: 1rem;
            cursor: pointer;
        }
        .input-area button:disabled { opacity: 0.5; }

        .dots {
            display: none; gap: 4px;
            padding: 0.7rem 1rem;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(167,139,250,0.2);
            border-radius: 1rem; align-self: flex-end;
        }
        .dots.show { display: flex; }
        .dot {
            width: 6px; height: 6px;
            background: #a78bfa; border-radius: 50%;
            animation: bounce 1.4s infinite;
        }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-8px); }
        }
    </style>
</head>
<body>
    <div class="header"><h1>✨ دستیار هوشمند ✨</h1></div>

    <div class="robot-container">
        <div class="robot-circle" id="robotCircle">
            <div class="eyes">
                <div class="eye"></div>
                <div class="eye"></div>
            </div>
            <div class="smile" id="smile"></div>
        </div>
        <div class="status" id="status">آماده‌ام! بپرس چی می‌خوای 🤗</div>
    </div>

    <div class="chat-box" id="chatBox"></div>

    <div class="input-area">
        <input type="text" id="input" placeholder="سوالت رو بنویس..." autocomplete="off">
        <button id="sendBtn" onclick="sendMessage()">بفرست</button>
    </div>

    <script>
        let conversation = [
            { role: "system", content: "تو یه دستیار دوستانه و بامزه هستی. جواب‌هات کوتاه، مفید و فارسی باشه." }
        ];

        const chatBox = document.getElementById("chatBox");
        const input = document.getElementById("input");
        const sendBtn = document.getElementById("sendBtn");
        const status = document.getElementById("status");
        const robotCircle = document.getElementById("robotCircle");
        const smile = document.getElementById("smile");

        input.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendMessage();
        });

        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;

            addMessage(text, "user");
            conversation.push({ role: "user", content: text });
            input.value = "";

            status.className = "status thinking";
            status.innerText = "دارم فکر می‌کنم...";
            robotCircle.classList.add("thinking");
            sendBtn.disabled = true;
            input.disabled = true;
            showDots();

            try {
                const res = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ messages: conversation })
                });

                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.error || "خطا در ارتباط");
                }

                const data = await res.json();
                const reply = data.reply;

                hideDots();
                addMessage(reply, "bot");
                conversation.push({ role: "assistant", content: reply });

                smile.classList.add("talking");
                setTimeout(() => smile.classList.remove("talking"), 2000);

                status.className = "status";
                status.innerText = "آماده‌ام! بپرس چی می‌خوای 🤗";
            } catch (e) {
                hideDots();
                addMessage("❌ خطا: " + e.message, "bot");
                status.className = "status";
                status.innerText = "مشکلی پیش اومد 😔";
            } finally {
                robotCircle.classList.remove("thinking");
                sendBtn.disabled = false;
                input.disabled = false;
                input.focus();
            }
        }

        function addMessage(text, sender) {
            const div = document.createElement("div");
            div.className = "msg " + sender;
            div.innerText = text;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function showDots() {
            const dots = document.createElement("div");
            dots.className = "dots show";
            dots.id = "thinkingDots";
            dots.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
            chatBox.appendChild(dots);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        function hideDots() {
            const d = document.getElementById("thinkingDots");
            if (d) d.remove();
        }

        input.focus();
    </script>
</body>
</html>
"""


# ============================================================
# مسیرها
# ============================================================

@app.route("/")
def home():
    return HOME_HTML


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        if not messages:
            return jsonify({"error": "پیامی ارسال نشد"}), 400

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://myrobot.app",
            "X-Title": "My Robot"
        }

        body = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }

        response = requests.post(API_URL, headers=headers, json=body, timeout=30)

        if not response.ok:
            err_msg = "خطا در OpenRouter"
            try:
                err_data = response.json()
                err_msg = err_data.get("error", {}).get("message", err_msg)
            except:
                pass
            return jsonify({"error": err_msg}), response.status_code

        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# اجرا
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 سرور روی پورت {port} اجرا شد")
    app.run(host="0.0.0.0", port=port)
