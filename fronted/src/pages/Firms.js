import React, { useEffect, useState } from "react";
import axios from "axios";
import FirmCard from "../components/FirmCard";

export default function Firms() {
  const [firms, setFirms] = useState([]);
  useEffect(() => {
    axios.get("http://localhost:8000/firmalar").then(res => setFirms(res.data));
  }, []);
  return (
    <div>
      <h2>Firmalar</h2>
      <div style={{display: "flex", flexWrap: "wrap", gap: "2rem"}}>
        {firms.map(f => <FirmCard key={f.id} firma={f} />)}
      </div>
    </div>
  );
}
