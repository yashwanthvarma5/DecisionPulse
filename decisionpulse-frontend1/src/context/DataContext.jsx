import { createContext, useContext, useState } from "react";

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <DataContext.Provider
      value={{
        result,
        setResult,
        loading,
        setLoading,
      }}
    >
      {children}
    </DataContext.Provider>
  );
}

export function useData() {
  return useContext(DataContext);
}
