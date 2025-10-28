import React from "react";
import { Card, CardContent, Typography } from "@mui/material";

export default function FirmCard({ firma }) {
  return (
    <Card sx={{ minWidth: 240, boxShadow: 3, background: "linear-gradient(135deg, #20c997 60%, #f8f9fa 100%)", color: "#273c75" }}>
      <CardContent>
        <Typography variant="h5">{firma.ad}</Typography>
        <Typography variant="subtitle1">{firma.sektor}</Typography>
        <Typography>Miktar: {firma.miktar} kg</Typography>
        <Typography>Fiyat: {firma.fiyat} TL/kg</Typography>
        <Typography>Temin Süresi: {firma.lead_time_days} gün</Typography>
      </CardContent>
    </Card>
  );
}
