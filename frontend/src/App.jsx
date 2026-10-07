import { useState } from "react";

const products = [
  { id: 1, name: "Wireless Headphones", price: 2499, category: "Electronics", icon: "🎧" },
  { id: 2, name: "Smart Watch", price: 3499, category: "Electronics", icon: "⌚" },
  { id: 3, name: "Running Shoes", price: 2999, category: "Fashion", icon: "👟" },
  { id: 4, name: "Laptop Backpack", price: 1499, category: "Accessories", icon: "🎒" },
  { id: 5, name: "Bluetooth Speaker", price: 1999, category: "Electronics", icon: "🔊" },
  { id: 6, name: "Cotton T-Shirt", price: 799, category: "Fashion", icon: "👕" },
];

function App() {
  const [cart, setCart] = useState([]);

  const addToCart = (product) => {
    setCart([...cart, product]);
  };

  return (
    <div style={{ minHeight: "100vh", background: "#f8fafc", fontFamily: "Arial, sans-serif" }}>
      <header style={{
        background: "#111827",
        color: "white",
        padding: "18px 7%",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center"
      }}>
        <h2 style={{ margin: 0 }}>🛍️ SmartShop</h2>
        <nav>
          <span style={{ marginRight: 25 }}>Home</span>
          <span style={{ marginRight: 25 }}>Products</span>
          <span style={{ marginRight: 25 }}>Orders</span>
          <span>🛒 Cart ({cart.length})</span>
        </nav>
      </header>

      <section style={{
        padding: "70px 7%",
        background: "linear-gradient(135deg, #2563eb, #7c3aed)",
        color: "white"
      }}>
        <h1 style={{ fontSize: 46, marginBottom: 15 }}>
          Smart Shopping Made Simple
        </h1>
        <p style={{ fontSize: 20 }}>
          Discover quality products, secure payments and easy order tracking.
        </p>
        <button style={{
          padding: "13px 25px",
          border: 0,
          borderRadius: 8,
          fontWeight: "bold",
          cursor: "pointer"
        }}>
          Shop Now
        </button>
      </section>

      <main style={{ padding: "45px 7%" }}>
        <h2>Featured Products</h2>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 22,
          marginTop: 25
        }}>
          {products.map((product) => (
            <div key={product.id} style={{
              background: "white",
              padding: 22,
              borderRadius: 12,
              boxShadow: "0 2px 10px rgba(0,0,0,.08)"
            }}>
              <div style={{ fontSize: 55, textAlign: "center", padding: 15 }}>
                {product.icon}
              </div>

              <small style={{ color: "#64748b" }}>
                {product.category}
              </small>

              <h3>{product.name}</h3>

              <strong style={{ fontSize: 20 }}>
                ₹{product.price.toLocaleString("en-IN")}
              </strong>

              <button
                onClick={() => addToCart(product)}
                style={{
                  width: "100%",
                  marginTop: 18,
                  padding: 11,
                  border: 0,
                  borderRadius: 7,
                  background: "#2563eb",
                  color: "white",
                  cursor: "pointer"
                }}
              >
                Add to Cart
              </button>
            </div>
          ))}
        </div>
      </main>

      <footer style={{
        marginTop: 40,
        padding: 25,
        textAlign: "center",
        background: "#111827",
        color: "white"
      }}>
        © 2026 SmartShop — Smart E-Commerce Platform
      </footer>
    </div>
  );
}

export default App;