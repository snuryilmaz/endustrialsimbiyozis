import React from "react";
import { Container, Typography, Box } from "@mui/material";

export default function Home() {
  return (
    <Box sx={{
      py: 8,
      background: "linear-gradient(180deg, #20c997 0%, #f8f9fa 100%)",
      color: "#273c75"
    }}>
      <Container maxWidth="md">
        <Typography variant="h2" fontWeight="bold" gutterBottom>
          Kaizuna: Sanayide Atığı Değere Dönüştüren Dijital Platform
        </Typography>
        <Typography variant="h5">
          Endüstriyel simbiyoz ile çevreye ve ekonomiye birlikte katkı sağlıyoruz.
        </Typography>
      </Container>
    </Box>
  );
}
