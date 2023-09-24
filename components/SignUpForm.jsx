import React, { useState } from "react";
import { Button, TextField } from "@mui/material";

function SignUpForm({ onSignUp }) {
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
    onSignUp(formData);
  };

  return (
    <div>
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
      <Button variant="contained" color="primary" onClick={handleSubmit}>
        Crear Cuenta
      </Button>
    </div>
  );
}

export default SignUpForm;
