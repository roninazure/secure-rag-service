export default function MessageBubble({ role, text }) {
  const isUser = role === "user";
  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} transition-all`}
    >
      <div
        className={`px-4 py-2 rounded-lg max-w-sm ${
          isUser
            ? "bg-blue-600 text-white rounded-br-none"
            : "bg-gray-300 text-black dark:bg-gray-700 dark:text-white rounded-bl-none"
        }`}
      >
        {text}
      </div>
    </div>
  );
}
