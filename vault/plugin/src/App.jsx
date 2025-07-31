import React from "react";
import EncryptionForm from "@ui/components/EncryptionForm";

const App = () => {
  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <h1 className="text-2xl font-bold mb-4">Vault Plugin</h1>
      <EncryptionForm />
    </div>
  );
};

export default App;
