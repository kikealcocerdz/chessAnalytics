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
  // Estado para almacenar el token de autenticación
  const [token, setToken] = useState(null);

  // Efecto que se ejecuta cuando la aplicación se carga
  useEffect(() => {
    // Realiza la autenticación cuando la aplicación se carga
    const loginData = {
      username: "tu_usuario",
      password: "tu_contraseña",
    };

    // Realiza una solicitud POST al servidor Flask para autenticar al usuario
    fetch("http://localhost:8080/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(loginData),
    })
      .then((response) => response.json())
      .then((data) => {
        // Almacena el token de acceso obtenido del servidor en el estado
        setToken(data.access_token);
      });
  }, []);

  const handleMostrarCrearCuenta = () => {
    setMostrarCrearCuenta(!mostrarCrearCuenta);
    setMostrarLogin(!mostrarLogin);
  };

  // Manejador para el botón de "Obtener datos"
  const handleLogin = () => {
    // Realiza una solicitud GET al servidor Flask para obtener datos
    fetch("http://localhost:8080/login", {
      headers: {
        Authorization: `Bearer ${token}`,
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
        return response.json();
      })
      .then((data) => {
        if (data) {
          // Almacena los datos obtenidos del servidor en el estado
          setInfo(data);
        }
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
    <div className="bg-chess-green">
      {mostrarLogin && (
        <div>
          <Typography variant="h4">Iniciar Sesión</Typography>
          <LoginForm onLogin={handleLogin} />
          <DataDisplay info={info} />
          <Button
            className="bg-chess-brown text-white"
            variant="contained"
            onClick={handleMostrarCrearCuenta}
          >
            {mostrarCrearCuenta ? "Iniciar Sesión" : "Crear Cuenta"}
          </Button>
        </div>
      )}
      {mostrarCrearCuenta && (
        <div>
          <Typography variant="h4">Crear Cuenta</Typography>
          <SignUpForm onSignUp={handleSignUp} />
          <Button
            className="bg-chess-brown text-white"
            variant="contained"
            onClick={handleMostrarCrearCuenta}
          >
            {mostrarCrearCuenta ? "Iniciar Sesión" : "Iniciar Sesión"}
          </Button>
        </div>
      )}
    </div>
  );
}

export default App;
