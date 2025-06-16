const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;
const DBS_FOLDER = path.join(__dirname, 'dbs');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));


// Ruta: guardar JSON localmente
app.post('/save/:username', (req, res) => {
    const { username } = req.params;
    const { points, reviews } = req.body;

    if (points === undefined || reviews === undefined) {
    return res.status(400).json({ success: false, message: 'Faltan datos points o reviews' });
}

    const userDir = path.join(DBS_FOLDER, username);
    if (!fs.existsSync(userDir)) fs.mkdirSync(userDir, { recursive: true });

    fs.writeFileSync(path.join(userDir, `${username}_points.json`), JSON.stringify(points, null, 2));
    fs.writeFileSync(path.join(userDir, `${username}_reviews.json`), JSON.stringify(reviews, null, 2));

    res.send(`Datos guardados para ${username}`);
});

// Ruta: cargar JSON desde disco
app.get('/load/:username', (req, res) => {
    const { username } = req.params;
    const userDir = path.join(DBS_FOLDER, username);

    try {
        const points = JSON.parse(fs.readFileSync(path.join(userDir, `${username}_points.json`)));
        const reviews = JSON.parse(fs.readFileSync(path.join(userDir, `${username}_reviews.json`)));
        res.json({ points, reviews });
    } catch (e) {
        res.status(404).send('Archivos no encontrados o error de lectura');
    }
});

function calcularNotasMedias() {
  const usuarios = fs.readdirSync(DBS_FOLDER).filter(dir =>
    fs.lstatSync(path.join(DBS_FOLDER, dir)).isDirectory()
  );

  const acumulado = {}; // ciudad -> categoría -> array de notas

  for (const usuario of usuarios) {
    const pointsPath = path.join(DBS_FOLDER, usuario, `${usuario}_points.json`);
    if (!fs.existsSync(pointsPath)) continue;

    const points = JSON.parse(fs.readFileSync(pointsPath, 'utf-8'));

    for (const [ciudad, categorias] of Object.entries(points)) {
      if (!acumulado[ciudad]) acumulado[ciudad] = {};

      for (const [clave, nota] of Object.entries(categorias)) {
        if (!acumulado[ciudad][clave]) acumulado[ciudad][clave] = [];
        acumulado[ciudad][clave].push(Number(nota));
      }
    }
  }

  const resultado = {};
  for (const [ciudad, categorias] of Object.entries(acumulado)) {
    resultado[ciudad] = {};
    let sumaTotal = 0;
    let totalCategorias = 0;

    for (const [clave, notas] of Object.entries(categorias)) {
      const media = notas.reduce((a, b) => a + b, 0) / notas.length;
      resultado[ciudad][clave] = Number(media.toFixed(2));
      sumaTotal += media;
      totalCategorias++;
    }

    if (totalCategorias > 0) {
      resultado[ciudad]["total"] = Number((sumaTotal / totalCategorias).toFixed(2));
    }
  }

  return resultado;
}


app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
});

app.post('/register', (req, res) => {
    const { username, password, email, ciudad } = req.body;

    if (!username || !password || !email || !ciudad) {
        return res.status(400).send('Faltan datos del perfil');
    }

    const userDir = path.join(DBS_FOLDER, username);
    if (!fs.existsSync(userDir)) fs.mkdirSync(userDir, { recursive: true });

    const profilePath = path.join(userDir, `${username}_profile.json`);

    if (fs.existsSync(profilePath)) {
        return res.status(409).send('El usuario ya existe');
    }

    // Crear profile.json
    const profile = { username, password, email, ciudad };
    fs.writeFileSync(profilePath, JSON.stringify(profile, null, 2), 'utf-8');

    // Crear points.json
    const pointsPath = path.join(userDir, `${username}_points.json`);
    fs.writeFileSync(pointsPath, JSON.stringify({}, null, 2), 'utf-8');

    // Crear reviews.json
    const reviewsPath = path.join(userDir, `${username}_reviews.json`);
    fs.writeFileSync(reviewsPath, JSON.stringify([], null, 2), 'utf-8');

    res.send('Usuario registrado correctamente con archivos iniciales');
});


app.post('/login', (req, res) => {
    const { username, password } = req.body;

    if (username === undefined || password === undefined) {
        return res.status(400).json({ success: false, message: 'Faltan datos en la petición' });
    }

    const profilePath = path.join(DBS_FOLDER, username, `${username}_profile.json`);
    if (!fs.existsSync(profilePath)) {
        return res.status(404).json({ success: false, message: 'Usuario no encontrado' });
    }

    const profile = JSON.parse(fs.readFileSync(profilePath, 'utf-8'));

    if (profile.password === password) {
        res.json({ success: true, username: profile.username });
    } else {
        res.json({ success: false, message: 'Contraseña incorrecta' });
    }
});

app.get('/api/general_data', (req, res) => {
  const general = calcularNotasMedias();

  // Guarda el resultado en general_data.json en la raíz del proyecto
  const outputPath = path.join(__dirname, 'general_data.json');
  fs.writeFileSync(outputPath, JSON.stringify(general, null, 2), 'utf-8');

  res.json(general);
});

app.get('/api/comentarios/:ciudad/:categoria', (req, res) => {
  const { ciudad, categoria } = req.params;
  const comentarios = [];

  // Lee todos los usuarios (carpetas en dbs)
  const usuarios = fs.readdirSync(DBS_FOLDER)
    .filter(dir => fs.lstatSync(path.join(DBS_FOLDER, dir)).isDirectory());

  for (const usuario of usuarios) {
    const reviewsPath = path.join(DBS_FOLDER, usuario, `${usuario}_reviews.json`);
    if (!fs.existsSync(reviewsPath)) continue;
    try {
      const reviews = JSON.parse(fs.readFileSync(reviewsPath, 'utf-8'));
      // Aquí revisa si hay comentarios para esa ciudad y categoría
      if (reviews[ciudad] && reviews[ciudad][categoria]) {
        comentarios.push({ usuario, comentario: reviews[ciudad][categoria] });
      }
    } catch (e) {
      // Si el archivo no es válido, ignora ese usuario
      continue;
    }
  }
  res.json(comentarios);
});





app.get('/api/all_users_data', (req, res) => {
  const usuarios = fs.readdirSync(DBS_FOLDER)
    .filter(dir => fs.lstatSync(path.join(DBS_FOLDER, dir)).isDirectory());

  const result = {};

  for (const usuario of usuarios) {
    const userDir = path.join(DBS_FOLDER, usuario);
    try {
      const points = JSON.parse(fs.readFileSync(path.join(userDir, `${usuario}_points.json`), 'utf-8'));
      const reviews = JSON.parse(fs.readFileSync(path.join(userDir, `${usuario}_reviews.json`), 'utf-8'));
      result[usuario] = { points, reviews };
    } catch (e) {
      // Ignora usuarios incompletos o error de parseo
    }
  }
  res.json(result);
});

app.get('/api/gepeto_reviews', (req, res) => {
  const reviewsPath = path.join(DBS_FOLDER, "Gepeto", "Gepeto_reviews.json");
  if (!fs.existsSync(reviewsPath)) {
    return res.status(404).json({ error: "No existe el archivo Gepeto_reviews" });
  }
  const reviews = JSON.parse(fs.readFileSync(reviewsPath, 'utf-8'));
  res.json(reviews);
});

app.get('/favicon.ico', (req, res) => res.status(204).end());
