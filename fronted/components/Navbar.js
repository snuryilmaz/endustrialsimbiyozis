import React from "react";
import { AppBar, Toolbar, Typography, Button } from "@mui/material";
import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <AppBar position="sticky" color="primary" elevation={4} style={{background: "linear-gradient(90deg, #20c997 0%, #2ecc71 100%)"}}>
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: "bold" }}>
          Kaizuna Platform
        </Typography>
        <Button color="inherit" component={Link} to="/">Ana Sayfa</Button>
        <Button color="inherit" component={Link} to="/about">Hakkımızda</Button>
        <Button color="inherit" component={Link} to="/firms">Firmalar</Button>
        <Button color="inherit" component={Link} to="/waste">Atıklar</Button>
        <Button color="inherit" component={Link} to="/subscribe">Abone Ol</Button>
        <Button color="inherit" component={Link} to="/faq">SSS</Button>
        <Button color="inherit" component={Link} to="/contact">İletişim</Button>
      </Toolbar>
    </AppBar>
  );
}
