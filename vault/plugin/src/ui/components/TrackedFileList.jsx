import React, { useEffect, useState } from "react";

const TrackedFileList = ({ safeSync }) => {
  const [files, setFiles] = useState([]);

  useEffect(() => {
    if (!safeSync) return;

    const updateFiles = () => {
      const tracked = safeSync.getTrackedFiles();
      setFiles([...tracked]); // Копия массива
    };

    updateFiles();

    const interval = setInterval(updateFiles, 2000); // Обновлять каждые 2 сек
    return () => clearInterval(interval);
  }, [safeSync]);

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-2">Синхронизируемые файлы</h3>
      <ul className="bg-gray-50 border rounded p-2 max-h-60 overflow-y-auto">
        {files.length === 0 && <li className="text-gray-400">Нет файлов</li>}
        {files.map((file, idx) => (
          <li key={idx} className="py-1 border-b last:border-0 flex justify-between items-center">
            <span className="text-sm">{file.name}</span>
            <span className="text-xs text-gray-600">
              {file.status || "в очереди"} ({(file.content.size / 1024).toFixed(1)} КБ)
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TrackedFileList;
