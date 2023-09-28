import React, { useState } from "react";
import { Button, TextField } from "@mui/material";

function LoginForm({ onLogin }) {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = () => {
    onLogin(formData);
  };

  return (
    <div className="text-white">
      <TextField
        label="Usuario"
        name="username"
        value={formData.username}
        onChange={handleInputChange}
        fullWidth
        margin="normal"
      />
      <TextField
        label="Contraseña"
        name="password"
        type="password"
        value={formData.password}
        onChange={handleInputChange}
        fullWidth
        margin="normal"
      />
      <button
        className="bg-chess-green p-4 rounded-xl text-white"
        onClick={handleSubmit}
      >
        Iniciar sesión
      </button>
    </div>
  );
}

export default LoginForm;
