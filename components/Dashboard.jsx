import { useState } from "react";
import { Navigate } from "react-router-dom";

export function Dashboard({token}) {
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

  const [stats_rapid, setStats_rapid] = useState("");
  const [stats_bullet, setStats_bullet] = useState("");
  const [stats_blitz, setStats_blitz] = useState("");
  const [stats_daily, setStats_daily] = useState("");

  const handleStats = async (event) => {
    event.preventDefault();

    const response = await fetch(
      `https://api.chess.com/pub/player/${username}/stats`
    );

    if (response.ok) {
      const data = await response.json();
      document.getElementById("pregunta").style.display = "none";
      setStats_rapid(data.chess_rapid.last.rating);
      setStats_bullet(data.chess_bullet.last.rating);
      setStats_blitz(data.chess_blitz.last.rating);
      setStats_daily(data.chess_daily.last.rating);
    } else {
      alert("Usuario no encontrado");
    }
  };

  // Utiliza el token para hacer solicitudes al servidor
  return (
    !token ? (
      <Navigate to="/" />
    ) : (
      <div className="bg-chess-black w-screen h-screen flex flex-col items-center justify-center">
        <div id="pregunta">
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
        </div>
        {chessUsername && (
          <div className="flex flex-col items-center h-screen w-screen bg-chess-black">
            <h3 className="text-chess-green">@{chessUsername}</h3>
            <img src={profileImage} alt="Profile" />
            <button
              className="bg-chess-green p-3 my-3 rounded-xl"
              onClick={handleStats}
            >
              Ver estadísticas
            </button>
            <div className="flex flex-col">
              <div className="flex">
                <h3 className="text-chess-green text-4xl p-5">
                  Rapid: {stats_rapid}
                </h3>
              </div>
              <div className="flex flex-col items-center p-5">
                <h3 className="text-chess-green text-4xl">
                  Bullet: {stats_bullet}
                </h3>
              </div>
              <div className="flex flex-col items-center p-5">
                <h3 className="text-chess-green text-4xl">
                  Blitz: {stats_blitz}
                </h3>
              </div>
              <div className="flex flex-col items-center p-5">
                <h3 className="text-chess-green text-4xl">
                  Daily: {stats_daily}
                </h3>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  );
}
