import React from 'react';

const FileList = ({ files }) => {
  if (!files || files.length === 0) {
    return <div className="text-gray-500">Нет зашифрованных файлов</div>;
  }

  return (
    <div>
      <h2 className="font-semibold mb-2">Отслеживаемые файлы:</h2>
      <ul className="border border-gray-300 rounded p-2 space-y-2">
        {files.map((file, index) => (
          <li key={index} className="flex justify-between items-center">
            <span className="text-sm">{file.fileName}</span>
            <span className="text-xs text-gray-600">{file.syncStatus}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FileList;
