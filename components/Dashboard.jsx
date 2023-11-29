import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useEffect } from "react";

export function Dashboard({ token, user_chess }) {
  const [chessUsername, setChessUsername] = useState("");
  const [profileImage, setProfileImage] = useState("");
  const [countryImage, setCountry] = useState("");
  let countryId = "";
  let countryCode = "";
  let countryFlag = "";

  useEffect(() => {
    async function fetchChessUser() {
      const response = await fetch(
        `https://api.chess.com/pub/player/${user_chess}`
      );

      if (response.ok) {
        const data = await response.json();
        setProfileImage(data.avatar);
        countryId = data.country;
        countryCode = countryId.code;
        countryCode = countryId.slice(-2);
        countryFlag = `https://flagsapi.com/${countryCode}/flat/64.png`;
        setCountry(countryFlag);
      } else {
        alert("Usuario no encontrado");
      }
    }

    fetchChessUser();
  }, []);

  const [stats_rapid, setStats_rapid] = useState("");
  const [stats_bullet, setStats_bullet] = useState("");
  const [stats_blitz, setStats_blitz] = useState("");
  const [stats_daily, setStats_daily] = useState("");
  const [buttonHidden, setButtonHidden] = useState(false);

  const handleStats = async (event) => {
    event.preventDefault();

    const response = await fetch(
      `https://api.chess.com/pub/player/${user_chess}/stats`
    );

    if (response.ok) {
      const data = await response.json();
      document.getElementById("pregunta").style.display = "none";
      setStats_rapid(data.chess_rapid.last.rating);
      setStats_bullet(data.chess_bullet.last.rating);
      setStats_blitz(data.chess_blitz.last.rating);
      setStats_daily(data.chess_daily.last.rating);
      setButtonHidden(true); // Ocultar el botón después de hacer clic
    } else {
      alert("Usuario no encontrado");
    }
  };

  const handleFirma = async (event) => {
    event.preventDefault();
    const response = await fetch("http://localhost:8080/firma", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        stats_blitz,
        stats_bullet,
        stats_daily,
        stats_rapid,
        user_chess,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      // Manejar la respuesta de /firma aquí
    } else {
      alert("No ha sido posible ejecutar la operación");
    }
  };
  // Utiliza el token para hacer solicitudes al servidor
  return !token ? (
    <Navigate to="/" />
  ) : (
    <div className="bg-chess-black w-screen h-screen flex flex-col items-center justify-center">
      <div id="pregunta">
        <h2 className="p-3 text-chess-green text-4xl text-center">CHESS.COM</h2>
      </div>
        <div className="flex flex-col items-center h-screen w-screen bg-chess-black">
          <h3 className="text-chess-green">@{user_chess}</h3>
          <img src={profileImage} alt="Profile" />
          <img src={countryImage} alt="Country" />
          {buttonHidden ?           <button
            className="bg-chess-green p-3 my-3 rounded-xl"
            onClick={handleFirma}
          >
            Obtener mis puntuaciones firmadas
          </button> : (
          <button
            className="bg-chess-green p-3 my-3 rounded-xl"
            onClick={handleStats}
          >
            Ver estadísticas
          </button>
          )}
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
    </div>
  );
}
