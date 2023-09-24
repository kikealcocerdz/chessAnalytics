import React, { useState, useEffect } from "react";
import { Button, Typography } from "@mui/material";
import "./App.css";
import LoginForm from "../components/LoginForm";
import DataDisplay from "../components/DataDisplay";
import SignUpForm from "../components/SignUpForm";

function App() {
  const [info, setInfo] = useState(null);
  const [token, setToken] = useState(null);

  useEffect(() => {
    // Realiza la autenticación cuando la aplicación se carga
    const loginData = {
      username: "tu_usuario",
      password: "tu_contraseña",
    };

    fetch("http://localhost:8080/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(loginData),
    })
      .then((response) => response.json())
      .then((data) => {
        setToken(data.access_token);
      });
  }, []);

  const handleLogin = () => {
    if (!token) {
      alert("No estás autenticado. Por favor, inicia sesión.");
      return;
    }

    fetch("http://localhost:8080/get_data", {
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
          setInfo(data);
        }
      });
  };

  const handleSignUp = (formData) => {
    // Realiza la solicitud para crear una cuenta
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
    <div>
      <Typography variant="h4">Iniciar Sesión</Typography>
      <LoginForm onLogin={handleLogin} />
      <Button onClick={handleLogin}>Obtener datos</Button>
      <DataDisplay info={info} />

      {/* Agrega el formulario de registro */}
      <Typography variant="h4">Crear Cuenta</Typography>
      <SignUpForm onSignUp={handleSignUp} />
    </div>
  );
}

export default App;
