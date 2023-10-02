import { useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { Dashboard } from "../components/Dashboard";

export function Login() {
  const [token, setToken] = useState(""); // [valor, funcion que actualiza el valor
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async (event) => {
    event.preventDefault();

    const response = await fetch("http://localhost:8080/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      setToken(data.token);
    } else {
      alert("Credenciales inválidas");
    }
  };

  if (token !== "") {
    console.log("estas en dashboard");
    return <Navigate to="/dashboard" />;
  }

  return (
    <div>
      <h2 className="p-3 text-chess-green text-4xl text-center">
        Iniciar sesión
      </h2>
      <form
        className="flex flex-col items-center text-center text-white"
        onSubmit={handleLogin}
      >
        <label className="flex flex-col">
          Nombre de usuario:
          <input
            className="text-black"
            type="text"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
        </label>
        <label className="flex flex-col">
          Contraseña:
          <input
            className="text-black"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        <button className="bg-chess-green p-3 my-3 rounded-xl" type="submit">
          Iniciar sesión
        </button>
      </form>
    </div>
  );
}

export function Signup() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSignup = async (event) => {
    event.preventDefault();

    const response = await fetch("http://localhost:8080/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      alert(data.message);
    } else {
      alert("Error al crear la cuenta. Por favor, inténtalo nuevamente.");
    }
  };

  return (
    <div>
      <h2 className="p-3 text-chess-green text-4xl text-center">
        Crear cuenta
      </h2>
      <form
        className="flex flex-col items-center text-center text-white"
        onSubmit={handleSignup}
      >
        <label className="flex flex-col">
          Nombre de usuario:
          <input
            className="text-black"
            type="text"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
        </label>
        <label className="flex flex-col">
          Contraseña:
          <input
            className="text-black"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        <button className="bg-chess-green p-3 my-3 rounded-xl" type="submit">
          Crear cuenta
        </button>
      </form>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <div className="bg-chess-black w-screen h-screen flex flex-col justify-center items-center">
            <Login />
            <Signup />
          </div>
        }
      />
      <Route path="/dashboard" element={<Dashboard />} />
    </Routes>
  );
}

export default App;
