"""Datos ficticios, idénticos a los de maquetas.html; no son datos descargados."""

PUBLISHERS = ["Norte de Tinta", "Lumbre Clara", "Orilla Interior", "Casa de Aliso"]

# Registro, publicación, título, autoría, editorial, género, color de portada.
SAMPLE_BOOKS = [
    ("REG-001", "2026-01-21", "El jardín de las horas", "Camila Valdés", PUBLISHERS[0], "Novela", "#7c866a"),
    ("REG-002", "2026-02-12", "Mapas para volver", "Diego Salvatierra", PUBLISHERS[0], "Novela", "#b78966"),
    ("REG-003", "2026-03-19", "La distancia del agua", "Lucía Ferrer", PUBLISHERS[1], "Relatos", "#698c91"),
    ("REG-004", "2026-05-07", "Los días de sal", "Mateo Alcázar", PUBLISHERS[1], "Novela", "#c09b69"),
    ("REG-005", "2026-07-09", "Un lugar entre las cosas", "Inés Robledo", PUBLISHERS[2], "Ensayo", "#8d8a77"),
    ("REG-006", "2026-09-03", "La casa de los tilos", "Camila Valdés", PUBLISHERS[0], "Novela", "#607d6c"),
    ("REG-007", "2026-09-07", "La ciudad de los faros", "Diego Salvatierra", PUBLISHERS[0], "Novela", "#7c9297"),
    ("REG-008", "2026-09-10", "Lo que trae la marea", "Lucía Ferrer", PUBLISHERS[1], "Relatos", "#b39073"),
    ("REG-009", "2026-09-14", "El invierno de las golondrinas", "Mateo Alcázar", PUBLISHERS[1], "Novela", "#8e827d"),
    ("REG-010", "2026-09-17", "La memoria de los objetos", "Inés Robledo", PUBLISHERS[2], "Ensayo", "#a6a071"),
    ("REG-011", "2026-09-24", "Cuaderno de la intemperie", "Adrián Montes", PUBLISHERS[3], "Poesía", "#7f8799"),
    ("REG-012", "2026-10-08", "El peso de la luz", "Adrián Montes", PUBLISHERS[3], "Poesía", "#b19d76"),
]

SOURCES = [
    {
        "id": "penguin",
        "name": "Penguin Libros",
        "kind": "Novedades de marzo",
        "url": "https://www.penguinlibros.com/es/recomendaciones/rankings/novedades-en-libros-de-marzo?recomendados=1",
        "domain": "penguinlibros.com",
        "description": "Selección mensual con enlaces a las fichas de los libros.",
        "limitation": "Es una selección editorial, no un registro completo de publicaciones.",
    },
    {
        "id": "planeta",
        "name": "Planeta de Libros",
        "kind": "Novedades editoriales",
        "url": "https://www.planetadelibros.com/libros-novedades",
        "domain": "planetadelibros.com",
        "description": "Listado de novedades y fichas técnicas para comprobar fecha e idioma.",
        "limitation": "Hay que distinguir idioma, formato, reediciones y títulos anunciados.",
    },
    {
        "id": "anagrama",
        "name": "Editorial Anagrama",
        "kind": "Boletín de novedades · PDF",
        "url": "https://cms.anagrama-ed.es/novedades.pdf",
        "domain": "cms.anagrama-ed.es",
        "description": "Boletín bibliográfico oficial con fechas de lanzamiento.",
        "limitation": "URL mutable: el boletín puede incluir lanzamientos futuros.",
    },
    {
        "id": "siruela",
        "name": "Ediciones Siruela",
        "kind": "Catálogo agosto–diciembre 2026 · PDF",
        "url": "https://www.siruela.com/archivos/Catalogo-b3_agosto-diciembre_2026_FERRO.pdf",
        "domain": "siruela.com",
        "description": "Catálogo de temporada con novedades organizadas por mes.",
        "limitation": "Una fecha mensual no permite confirmar el día exacto de publicación.",
    },
]
