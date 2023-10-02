import { useState } from "react";

export function Dashboard() {
  const [username, setUsername] = useState("");
  const [chessUsername, setChessUsername] = useState("");
  const [profileImage, setProfileImage] = useState("");

  async function handleChessUser(event) {
    event.preventDefault();

    const response = await fetch(
      `https://api.chess.com/pub/player/${username}`
    );

    if (response.ok) {
      const data = await response.json();
      setChessUsername(data.username);
      setProfileImage(data.avatar);
    } else {
      alert("Usuario no encontrado");
    }
  }

  // Utiliza el token para hacer solicitudes al servidor
  return (
    <div className="bg-chess-black w-screen h-screen flex flex-col items-center justify-center">
      <h2 className="p-3 text-chess-green text-4xl text-center">CHESS.COM</h2>
      <form
        className="flex flex-col items-center text-center text-white"
        onSubmit={handleChessUser}
      >
        <label className="flex flex-col">
          Nombre de usuario de Chess.com:
          <input
            className="text-black"
            type="text"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
        </label>
        <button className="bg-chess-green p-3 my-3 rounded-xl" type="submit">
          Buscar
        </button>
      </form>
      {chessUsername && (
        <div className="flex flex-col items-center">
          <h3 className="text-chess-green">¿Es esta tu foto de perfil?</h3>
          <img src={profileImage} alt="Profile" />
        </div>
      )}
    </div>
  );
}
