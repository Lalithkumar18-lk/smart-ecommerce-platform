
import { useState } from "react";
import "./App.css";

const products = [
  { id: 1, name: "Wireless Headphones", category: "Electronics", price: 2499, image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80" },
  { id: 2, name: "Smart Watch", category: "Electronics", price: 3299, image: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80" },
  { id: 3, name: "Everyday Backpack", category: "Fashion", price: 1499, image: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80" },
  { id: 4, name: "Running Sneakers", category: "Fashion", price: 2199, image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80" },
  { id: 5, name: "Coffee Maker", category: "Home", price: 1899, image: "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=800&q=80" },
  { id: 6, name: "Desk Lamp", category: "Home", price: 899, image: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80" },
  { id: 7, name: "Bluetooth Speaker", category: "Electronics", price: 1799, image: "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=800&q=80" },
  { id: 8, name: "Classic Sunglasses", category: "Fashion", price: 999, image: "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=800&q=80" },
];

export default function App() {
  const [category, setCategory] = useState("All");
  const [search, setSearch] = useState("");
  const [cart, setCart] = useState({});

  const filtered = products.filter(p =>
    (category === "All" || p.category === category) &&
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  const count = Object.values(cart).reduce((a, b) => a + b, 0);
  const total = products.reduce((sum, p) => sum + p.price * (cart[p.id] || 0), 0);
  const money = n => "₹" + n.toLocaleString("en-IN");

  function addToCart(id, change = 1) {
    setCart(old => ({ ...old, [id]: Math.max(0, (old[id] || 0) + change) }));
  }

  return (
    <div className="app">
      <div className="topline">✨ Discover something you'll love · Welcome to ShopSmart</div>
      <header className="navbar">
        <a className="brand" href="#">🛍️ ShopSmart</a>
        <input className="searchbox" placeholder="Search products..." value={search} onChange={e => setSearch(e.target.value)} />
        <button className="cart-button" onClick={() => document.getElementById("cart").scrollIntoView({ behavior: "smooth" })}>Cart ({count})</button>
      </header>

      <main>
        <section className="hero">
          <div>
            <div className="eyebrow">THE SMART WAY TO SHOP</div>
            <h1>Good finds.<br />Better <span>everyday.</span></h1>
            <p>Discover electronics, fashion, and home essentials for everyday life.</p>
            <button className="primary-button" onClick={() => document.getElementById("products").scrollIntoView({ behavior: "smooth" })}>Explore products ↗</button>
          </div>
          <div className="hero-art">
            <div className="art-card">🎧<small>Tech essentials</small></div>
            <div className="art-card">👟<small>Everyday style</small></div>
            <div className="art-card">☕<small>Home comforts</small></div>
          </div>
        </section>

        <section className="catalog" id="products">
          <div className="section-heading">
            <div><div className="eyebrow">OUR COLLECTION</div><h2>Find your favorites</h2></div>
            <span>{filtered.length} products</span>
          </div>
          <div className="filters">
            {["All", "Electronics", "Fashion", "Home"].map(c =>
              <button key={c} className={category === c ? "filter active" : "filter"} onClick={() => setCategory(c)}>{c}</button>
            )}
          </div>
          <div className="product-grid">
            {filtered.map(p => (
              <article className="product-card" key={p.id}>
                <div className="product-art">
                  <img className="product-photo" src={p.image} alt={p.name} />
                </div>
                <div className="product-info">
                  <div className="product-category">{p.category}</div>
                  <h3>{p.name}</h3>
                  <div className="product-bottom"><strong>{money(p.price)}</strong><span>★ 4.7</span></div>
                  <button className="add-button" onClick={() => addToCart(p.id)}>Add to cart ＋</button>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="catalog" id="cart">
          <div className="section-heading"><div><div className="eyebrow">YOUR SELECTION</div><h2>Your shopping cart</h2></div></div>
          {products.filter(p => cart[p.id] > 0).length === 0 ? <p>Your cart is empty. Add a product above to get started.</p> :
            products.filter(p => cart[p.id] > 0).map(p => (
              <div className="cart-row" key={p.id}>
                <span>{p.name}</span>
                <button onClick={() => addToCart(p.id, -1)}>−</button>
                <span>{cart[p.id]}</span>
                <button onClick={() => addToCart(p.id, 1)}>＋</button>
                <strong>{money(p.price * cart[p.id])}</strong>
              </div>
            ))
          }
          <h3>Subtotal: {money(total)}</h3>
          <p className="notice">Demo checkout only. No payment is processed.</p>
        </section>
      </main>
      <footer><h3>ShopSmart</h3><p>Everyday finds for everyone.</p><small>© 2026 ShopSmart · Demo storefront</small></footer>
    </div>
  );
}