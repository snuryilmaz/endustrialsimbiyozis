import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Subscribe from "./pages/Subscribe";
import FAQ from "./pages/FAQ";
import Firms from "./pages/Firms";
import Waste from "./pages/Waste";

const theme = createTheme({
  palette: {
    primary: { main: "#20c997" },
    secondary: { main: "#273c75" },
    background: { default: "#f8f9fa" }
  },
  typography: { fontFamily: "Montserrat, sans-serif" }
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/subscribe" element={<Subscribe />} />
          <Route path="/faq" element={<FAQ />} />
          <Route path="/firms" element={<Firms />} />
          <Route path="/waste" element={<Waste />} />
        </Routes>
        <Footer />
      </Router>
    </ThemeProvider>
  );
}
export default App;
