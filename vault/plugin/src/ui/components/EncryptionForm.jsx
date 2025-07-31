import React, { useState, useRef } from "react";
import CryptoEngine from "@/core/crypto/CryptoEngine";
import SafeSync from "@/core/transport/SafeSync";
import TrackedFileList from "./TrackedFileList";

const EncryptionForm = () => {
  const [file, setFile] = useState(null);
  const [word, setWord] = useState("");
  const [gesture, setGesture] = useState(""); // пока текстом
  const [status, setStatus] = useState("");

  const safeSync = useRef(new SafeSync());
  const cryptoEngine = useRef(new CryptoEngine());

  const handleEncryptAndUpload = async () => {
    if (!file || !word || !gesture) {
      setStatus("Заполните все поля");
      return;
    }

    setStatus("Шифрование...");
    try {
      const timestamp = Date.now().toString();
      const key = await cryptoEngine.current.deriveKey(word, gesture, timestamp);

      const { encrypted, hmac, nonce } = await cryptoEngine.current.encryptFile(file, key);

      const result = await safeSync.current.trackAndUpload({
        originalFile: file,
        encryptedFile: encrypted,
        meta: { hmac, nonce, gesture, word, timestamp },
      });

      setStatus(result.success ? "Файл зашифрован и загружен" : "Ошибка загрузки");
    } catch (err) {
      console.error(err);
      setStatus("Ошибка шифрования или загрузки");
    }
  };

  return (
    <div className="max-w-xl mx-auto p-4 bg-white rounded shadow">
      <h1 className="text-xl font-bold mb-4">Зашифровать файл</h1>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-2"
      />

      <input
        type="text"
        placeholder="Секретное слово"
        value={word}
        onChange={(e) => setWord(e.target.value)}
        className="w-full mb-2 p-2 border rounded"
      />

      <input
        type="text"
        placeholder="Жест (текстово)"
        value={gesture}
        onChange={(e) => setGesture(e.target.value)}
        className="w-full mb-2 p-2 border rounded"
      />

      <button
        onClick={handleEncryptAndUpload}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Зашифровать и загрузить
      </button>

      <div className="mt-4 text-sm text-gray-600">{status}</div>

      {/* Список отслеживаемых файлов */}
      <TrackedFileList safeSync={safeSync.current} />
    </div>
  );
};

export default EncryptionForm;
