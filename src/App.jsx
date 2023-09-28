import React, { useState, useEffect } from "react";
import { Button, Typography } from "@mui/material";
import "./index.css";
import LoginForm from "../components/LoginForm";
import DataDisplay from "../components/DataDisplay";
import SignUpForm from "../components/SignUpForm";

function App() {
  // Estado para almacenar la información obtenida del servidor
  const [info, setInfo] = useState(null);
  const [mostrarCrearCuenta, setMostrarCrearCuenta] = useState(false);
  const [mostrarLogin, setMostrarLogin] = useState(true);
  const [logged, setLogged] = useState(false);
  // Estado para almacenar el token de autenticación
  const [token, setToken] = useState(null);

  const handleMostrarCrearCuenta = () => {
    setMostrarCrearCuenta(!mostrarCrearCuenta);
    setMostrarLogin(!mostrarLogin);
  };

  // Manejador para el botón de "Obtener datos"
  const handleLogin = () => {
    // Realiza una solicitud GET al servidor Flask para obtener datos
    fetch("http://localhost:8080/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (response.status === 401) {
          alert(
            "Token de acceso no válido. Por favor, inicia sesión nuevamente."
          );
          setToken(null);
          return null;
        }
        if (response.ok) {
          // Almacena la información obtenida del servidor en el estado
          console.log("logeado");
          setLogged(true);
        }
      })
      .catch((error) => {
        alert(
          "Hubo un error al iniciar sesión. Por favor, inténtalo más tarde."
        );
      });
  };

  // Manejador para el formulario de registro
  const handleSignUp = (formData) => {
    // Realiza una solicitud POST al servidor Flask para crear una cuenta
    fetch("http://localhost:8080/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    })
      .then((response) => {
        if (response.ok) {
          alert("Cuenta creada exitosamente. Ahora puedes iniciar sesión.");
        } else {
          alert("Error al crear la cuenta. Por favor, inténtalo nuevamente.");
        }
      })
      .catch((error) => {
        alert(
          "Hubo un error al crear la cuenta. Por favor, inténtalo más tarde."
        );
      });
  };

  return (
    <div className="bg-chess-black h-screen flex items-center text-white w-screen font-serif">
      {logged ? (
        <div>
          <h2 className="text-6xl">BUENOS DIAS CHESS</h2>
        </div>
      ) : (
        <>
          {mostrarLogin && (
            <div>
              <h2 className="text-4xl text-center p-5">Iniciar Sesión</h2>
              <div className="flex flex-col items-center w-screen">
                <LoginForm onLogin={handleLogin} />
                <button
                  className="bg-chess-green p-1 rounded-lg text-white"
                  onClick={handleMostrarCrearCuenta}
                >
                  {mostrarCrearCuenta ? "Iniciar Sesión" : "Crear Cuenta"}
                </button>
              </div>
            </div>
          )}
          {mostrarCrearCuenta && (
            <div>
              <h2 className="text-4xl text-center p-5">Crea tu cuenta</h2>
              <div className="flex flex-col items-center w-screen">
                <SignUpForm onSignUp={handleSignUp} />
                <button
                  className="bg-chess-green p-1 rounded-lg text-white max-w-lg"
                  onClick={handleMostrarCrearCuenta}
                >
                  {mostrarCrearCuenta ? "Iniciar Sesión" : "Iniciar Sesión"}
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
