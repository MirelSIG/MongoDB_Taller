INDEX_HTML = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>MongoDB Atlas Demo</title>
  <style>
    :root {
      --bg: #f4efe6;
      --card: #fffdf8;
      --ink: #1f2933;
      --accent: #0f766e;
      --accent-2: #c2410c;
      --line: #d6cec2;
    }
    body {
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      background: radial-gradient(circle at top right, #f8e4c9, var(--bg));
      color: var(--ink);
    }
    .wrap {
      max-width: 900px;
      margin: 32px auto;
      padding: 0 16px;
    }
    .hero {
      border: 1px solid var(--line);
      background: var(--card);
      border-radius: 18px;
      padding: 20px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
    }
    h1 {
      margin: 0 0 8px;
      font-size: 1.8rem;
    }
    .row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 14px;
      margin-top: 16px;
    }
    .card {
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px;
      background: #fff;
    }
    button {
      border: 0;
      border-radius: 8px;
      padding: 8px 12px;
      background: var(--accent);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
    }
    button.secondary {
      background: var(--accent-2);
    }
    pre {
      background: #111827;
      color: #e5e7eb;
      padding: 12px;
      border-radius: 10px;
      overflow: auto;
      min-height: 180px;
    }
    code {
      color: #0b5f59;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>Demo Flask + MongoDB Atlas</h1>
      <p>
        Bases Atlas:
        <code>matricula={{ db_matricula }}</code>,
        <code>docentes={{ db_docentes }}</code>,
        <code>socios={{ db_socios }}</code>,
        <code>proveedores={{ db_proveedores }}</code>
      </p>
      <p>1) Carga datos con <code>/seed</code> y 2) prueba endpoints de consulta y agregacion.</p>
      <div class="row">
        <div class="card">
          <h3>Seed de datos</h3>
          <p>Importa NDJSON de MONGODB_TALLER a Atlas.</p>
          <button onclick="run('/seed', 'POST')">POST /seed</button>
        </div>
        <div class="card">
          <h3>Socios por ciudad</h3>
          <p>Filtra por Bilbao o Vitoria.</p>
          <button onclick="run('/api/socios?ciudad=Bilbao')">GET /api/socios?ciudad=Bilbao</button>
        </div>
        <div class="card">
          <h3>Lookup proveedores-socios</h3>
          <p>Relacion simple por ciudad usando <code>$lookup</code>.</p>
          <button class="secondary" onclick="run('/api/join/proveedores-socios')">GET /api/join/proveedores-socios</button>
        </div>
      </div>
    </section>
    <h3>Salida</h3>
    <pre id="out">Pulsa un boton para ejecutar una llamada.</pre>
  </div>
<script>
  async function run(url, method = 'GET') {
    const out = document.getElementById('out');
    out.textContent = 'Cargando...';
    try {
      const res = await fetch(url, { method });
      const data = await res.json();
      out.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
      out.textContent = String(err);
    }
  }
</script>
</body>
</html>
"""
