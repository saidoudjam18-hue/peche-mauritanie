from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
import functools
import os

app = Flask(__name__)
app.secret_key = 'mld_secret_key_2026_secure'
app.config['UPLOAD_FOLDER'] = 'static/documents'

# =============================
# CONFIGURATION
# =============================
USERS = {
    'maouloud': 'omng'
}

TRANSLATIONS = {
    'fr': {
        'dashboard': 'Tableau de bord',
        'associations': 'Associations',
        'cotisations': 'Cotisations',
        'reunions': 'Réunions',
        'objets': 'Objets',
        'bureau': 'Bureau',
        'documents': 'Documents',
        'logout': 'Déconnexion',
        'total_associations': 'Total Associations',
        'total_cotisations': 'Total Cotisations',
        'total_reunions': 'Total Réunions',
        'total_objets': 'Total Objets',
        'total_money': 'Total Argent',
        'add_new': 'Ajouter',
        'name': 'Nom',
        'role': 'Fonction / Rôle',
        'file': 'Fichier',
        'download': 'Télécharger',
        'amount': 'Montant',
        'date': 'Date',
        'place': 'Lieu',
        'quantity': 'Quantité',
        'actions': 'Actions',
        'save': 'Enregistrer',
        'cancel': 'Annuler',
        'welcome': 'Bienvenue',
        'login_error': 'Nom d\'utilisateur ou mot de passe incorrect',
        'search': 'Rechercher...',
        'member': 'Membre',
        'expenses': 'Dépenses',
        'withdrawals': 'Retraits',
        'reason': 'Motif',
        'total_expenses': 'Total Dépenses',
        'balance': 'Solde Restant',
        'withdraw': 'Retirer',
    },
    'ar': {
        'dashboard': 'لوحة القيادة',
        'associations': 'الجمعيات',
        'cotisations': 'الاشتراكات',
        'reunions': 'الاجتماعات',
        'objets': 'الكائنات',
        'bureau': 'المكتب',
        'documents': 'المستندات',
        'logout': 'تسجيل الخروج',
        'total_associations': 'إجمالي الجمعيات',
        'total_cotisations': 'إجمالي الاشتراكات',
        'total_reunions': 'إجمالي الاجتماعات',
        'total_objets': 'إجمالي الكائنات',
        'total_money': 'إجمالي الأموال',
        'add_new': 'إضافة',
        'name': 'الاسم',
        'role': 'الوظيفة',
        'file': 'الملف',
        'download': 'تحميل',
        'amount': 'المبلغ',
        'date': 'التاريخ',
        'place': 'المكان',
        'quantity': 'الكمية',
        'actions': 'إجراءات',
        'save': 'حفظ',
        'cancel': 'إلغاء',
        'welcome': 'مرحبًا',
        'login_error': 'اسم المستخدم أو كلمة المرور غير صحيحة',
        'search': 'بحث...',
        'member': 'عضو',
        'expenses': 'نفقات',
        'withdrawals': 'سحوبات',
        'reason': 'السبب',
        'total_expenses': 'إجمالي النفقات',
        'balance': 'الرصيد المتبقي',
        'withdraw': 'سحب',
    }
}

# =============================
# DATABASE (SQLite)
# =============================
DATABASE = 'mld.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Access columns by name
    return db, db.cursor()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database with tables and default data."""
    with app.app_context():
        db, cursor = get_db()
        # Create Tables
        cursor.execute('''CREATE TABLE IF NOT EXISTS Association (
            id_association INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Cotisation (
            id_cotisation INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_membre TEXT,
            montant REAL,
            date_paiement TEXT,
            id_association INTEGER,
            FOREIGN KEY (id_association) REFERENCES Association(id_association)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Reunion (
            id_reunion INTEGER PRIMARY KEY AUTOINCREMENT,
            date_reunion TEXT,
            lieu TEXT,
            id_association INTEGER,
            FOREIGN KEY (id_association) REFERENCES Association(id_association)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Objets (
            id_objet INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_objet TEXT,
            quantite INTEGER,
            id_association INTEGER,
            FOREIGN KEY (id_association) REFERENCES Association(id_association)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Depense (
            id_depense INTEGER PRIMARY KEY AUTOINCREMENT,
            motif TEXT,
            montant REAL,
            date_depense TEXT,
            id_association INTEGER,
            FOREIGN KEY (id_association) REFERENCES Association(id_association)
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS Bureau (
            id_membre INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            role TEXT,
            telephone TEXT,
            id_association INTEGER,
            FOREIGN KEY (id_association) REFERENCES Association(id_association)
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS Documents (
            id_document INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT,
            fichier TEXT,
            date_ajout TEXT,
            id_association INTEGER,
            FOREIGN KEY (id_association) REFERENCES Association(id_association)
        )''')
        
        # Check if associations exist
        cursor.execute("SELECT COUNT(*) FROM Association")
        if cursor.fetchone()[0] == 0:
            associations = [
                ('Houda',), ('Timtimol',), ('Bamtaare Ngoral',),
                ('Yiilibe bamtaare',), ('U.J.D.S.family',), ('Dental googa',), ('O.M.N.G',)
            ]
            cursor.executemany("INSERT INTO Association (nom) VALUES (?)", associations)
            db.commit()
        else:
            # Ensure O.M.N.G exists even if DB already exists
            cursor.execute("SELECT COUNT(*) FROM Association WHERE nom = 'O.M.N.G'")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO Association (nom) VALUES ('O.M.N.G')")
                db.commit()

# Initialize DB on start (simple check)
if not os.path.exists(DATABASE):
    init_db()


# =============================
# AUTHENTICATION & CONTEXT
# =============================
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

@app.context_processor
def inject_context():
    lang = session.get('lang', 'fr')
    return dict(
        current_lang=lang, 
        translations=TRANSLATIONS.get(lang, TRANSLATIONS['fr'])
    )

# =============================
# ROUTES
# =============================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip() # Trim whitespace
        password = request.form["password"].strip()
        
        if username in USERS and USERS[username] == password:
            session['user'] = username
            session['lang'] = 'fr'  # Default lang
            return redirect(url_for('dashboard'))
        else:
            flash(TRANSLATIONS['fr']['login_error'], 'error')
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/set_language", methods=["POST"])
def set_language():
    lang = request.form.get('lang')
    if lang in TRANSLATIONS:
        session['lang'] = lang
    return redirect(request.referrer or url_for('dashboard'))

@app.route("/")
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
@login_required
def dashboard():
    db, cursor = get_db()
    
    cursor.execute("SELECT COUNT(*) as total FROM Association")
    associations = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM Cotisation")
    cotisations = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM Reunion")
    reunions = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM Objets")
    objets = cursor.fetchone()["total"]

    cursor.execute("SELECT SUM(montant) as total FROM Cotisation")
    res = cursor.fetchone()
    # Handle None result safely
    argent = res["total"] if res and res["total"] is not None else 0

    # Calculate Expenses
    cursor.execute("SELECT SUM(montant) as total FROM Depense")
    res_dep = cursor.fetchone()
    total_depenses = res_dep["total"] if res_dep and res_dep["total"] is not None else 0

    # Calculate Balance
    solde = argent - total_depenses

    # Chart Data
    cursor.execute("""
        SELECT a.nom, SUM(c.montant) AS total
        FROM Cotisation c
        JOIN Association a
        ON a.id_association=c.id_association
        GROUP BY a.nom
    """)
    stats = cursor.fetchall()

    labels = [s["nom"] for s in stats]
    valeurs = [float(s["total"]) if s["total"] else 0 for s in stats]

    return render_template(
        "dashboard.html",
        associations=associations,
        cotisations=cotisations,
        reunions=reunions,
        objets=objets,
        argent=argent,
        labels=labels,
        valeurs=valeurs,
        total_depenses=total_depenses,
        solde=solde,
        associations_list=cursor.execute("SELECT * FROM Association").fetchall()
    )

@app.route("/depenses")
@login_required
def depenses():
    db, cursor = get_db()
    cursor.execute("""
        SELECT d.*, a.nom AS association
        FROM Depense d
        JOIN Association a
        ON d.id_association=a.id_association
    """)
    data = cursor.fetchall()

    cursor.execute("SELECT * FROM Association")
    associations = cursor.fetchall()

    return render_template(
        "depenses.html",
        depenses=data,
        associations=associations
    )

@app.route("/ajouter_depense", methods=["POST"])
@login_required
def ajouter_depense():
    db, cursor = get_db()
    motif = request.form["motif"]
    montant = request.form["montant"]
    date = request.form["date_depense"]
    association = request.form["id_association"]

    cursor.execute("""
        INSERT INTO Depense(motif, montant, date_depense, id_association)
        VALUES (?,?,?,?)
    """, (motif, montant, date, association))

    db.commit()
    flash('Dépense enregistrée!', 'success')
    return redirect(url_for("depenses"))

@app.route("/associations")
@login_required
def associations():
    db, cursor = get_db()
    cursor.execute("SELECT * FROM Association")
    data = cursor.fetchall()
    return render_template("associations.html", associations=data)

@app.route("/ajouter_association", methods=["POST"])
@login_required
def ajouter_association():
    db, cursor = get_db()
    nom = request.form["nom"]
    cursor.execute("INSERT INTO Association(nom) VALUES(?)", (nom,))
    db.commit()
    flash('Association ajoutée avec succès!', 'success')
    return redirect(url_for("associations"))

@app.route("/cotisations")
@login_required
def cotisations():
    db, cursor = get_db()
    cursor.execute("""
        SELECT c.*, a.nom AS association
        FROM Cotisation c
        JOIN Association a
        ON c.id_association=a.id_association
    """)
    data = cursor.fetchall()

    cursor.execute("SELECT * FROM Association")
    associations = cursor.fetchall()

    return render_template(
        "cotisations.html",
        cotisations=data,
        associations=associations
    )

@app.route("/ajouter_cotisation", methods=["POST"])
@login_required
def ajouter_cotisation():
    db, cursor = get_db()
    nom = request.form["nom_membre"]
    montant = request.form["montant"]
    date = request.form["date_paiement"]
    association = request.form["id_association"]

    cursor.execute("""
        INSERT INTO Cotisation
        (nom_membre, montant, date_paiement, id_association)
        VALUES (?,?,?,?)
    """, (nom, montant, date, association))

    db.commit()
    flash('Cotisation ajoutée!', 'success')
    return redirect(url_for("cotisations"))

@app.route("/reunions")
@login_required
def reunions():
    db, cursor = get_db()
    cursor.execute("""
        SELECT r.*, a.nom AS association
        FROM Reunion r
        JOIN Association a
        ON r.id_association=a.id_association
    """)
    reunions = cursor.fetchall()

    cursor.execute("SELECT * FROM Association")
    associations = cursor.fetchall()

    return render_template(
        "reunions.html",
        reunions=reunions,
        associations=associations
    )

@app.route("/ajouter_reunion", methods=["POST"])
@login_required
def ajouter_reunion():
    db, cursor = get_db()
    date = request.form["date_reunion"]
    lieu = request.form["lieu"]
    association = request.form["id_association"]

    cursor.execute("""
        INSERT INTO Reunion(date_reunion, lieu, id_association)
        VALUES (?,?,?)
    """, (date, lieu, association))

    db.commit()
    flash('Réunion planifiée!', 'success')
    return redirect(url_for("reunions"))

@app.route("/objets")
@login_required
def objets():
    db, cursor = get_db()
    cursor.execute("""
        SELECT o.*, a.nom AS association
        FROM Objets o
        JOIN Association a
        ON o.id_association=a.id_association
    """)
    objets = cursor.fetchall()

    cursor.execute("SELECT * FROM Association")
    associations = cursor.fetchall()

    return render_template(
        "objets.html",
        objets=objets,
        associations=associations
    )

@app.route("/ajouter_objet", methods=["POST"])
@login_required
def ajouter_objet():
    db, cursor = get_db()
    nom = request.form["nom_objet"]
    quantite = request.form["quantite"]
    association = request.form["id_association"]

    cursor.execute("""
        INSERT INTO Objets(nom_objet, quantite, id_association)
        VALUES (?,?,?)
    """, (nom, quantite, association))

    db.commit()
    flash('Objet ajouté!', 'success')
    return redirect(url_for("objets"))

@app.route("/bureau")
@login_required
def bureau():
    db, cursor = get_db()
    cursor.execute("""
        SELECT b.*, a.nom AS association
        FROM Bureau b
        JOIN Association a
        ON b.id_association=a.id_association
    """)
    membres = cursor.fetchall()
    
    cursor.execute("SELECT * FROM Association")
    associations = cursor.fetchall()

    return render_template("bureau.html", membres=membres, associations=associations)

@app.route("/ajouter_membre_bureau", methods=["POST"])
@login_required
def ajouter_membre_bureau():
    db, cursor = get_db()
    nom = request.form["nom"]
    role = request.form["role"]
    telephone = request.form.get("telephone", "")
    association = request.form["id_association"]

    cursor.execute("""
        INSERT INTO Bureau(nom, role, telephone, id_association)
        VALUES (?,?,?,?)
    """, (nom, role, telephone, association))
    
    db.commit()
    flash('Membre ajouté au bureau!', 'success')
    return redirect(url_for("bureau"))

@app.route("/documents")
@login_required
def documents():
    db, cursor = get_db()
    cursor.execute("""
        SELECT d.*, a.nom AS association
        FROM Documents d
        JOIN Association a
        ON d.id_association=a.id_association
    """)
    documents = cursor.fetchall()
    
    cursor.execute("SELECT * FROM Association")
    associations = cursor.fetchall()

    return render_template("documents.html", documents=documents, associations=associations)

from werkzeug.utils import secure_filename

@app.route("/ajouter_document", methods=["POST"])
@login_required
def ajouter_document():
    db, cursor = get_db()
    titre = request.form["titre"]
    association = request.form["id_association"]
    date_ajout = request.form["date_ajout"]
    
    if 'fichier' not in request.files:
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('documents'))
        
    file = request.files['fichier']
    if file.filename == '':
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('documents'))

    if file:
        filename = secure_filename(file.filename)
        # Ensure directory exists (redundant safety)
        os.makedirs('static/documents', exist_ok=True)
        file.save(os.path.join('static/documents', filename))
        
        cursor.execute("""
            INSERT INTO Documents(titre, fichier, date_ajout, id_association)
            VALUES (?,?,?,?)
        """, (titre, filename, date_ajout, association))
        
        db.commit()
        flash('Document ajouté avec succès!', 'success')
        
    return redirect(url_for("documents"))

@app.route("/fix_db")
def fix_db():
    try:
        db, cursor = get_db()
        # Create Tables
        cursor.execute('''CREATE TABLE IF NOT EXISTS Association (
            id_association INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Cotisation (
            id_cotisation INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_membre TEXT,
            montant REAL,
            date_paiement TEXT,
            id_association INTEGER,
            FOREIGN KEY (id_association) REFERENCES Association(id_association)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Reunion (
            id_reunion INTEGER PRIMARY KEY AUTOINCREMENT,
            date_reunion TEXT,
            lieu TEXT,
            id_association INTEGER,
            FOREIGN KEY (id_association) REFERENCES Association(id_association)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Objets (
            id_objet INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_objet TEXT,
            quantite INTEGER,
            id_association INTEGER,
            FOREIGN KEY (id_association) REFERENCES Association(id_association)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Depense (
            id_depense INTEGER PRIMARY KEY AUTOINCREMENT,
            motif TEXT,
            montant REAL,
            date_depense TEXT,
            id_association INTEGER,
            FOREIGN KEY (id_association) REFERENCES Association(id_association)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Bureau (
            id_membre INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            role TEXT,
            telephone TEXT,
            id_association INTEGER,
            FOREIGN KEY (id_association) REFERENCES Association(id_association)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Documents (
            id_document INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT,
            fichier TEXT,
            date_ajout TEXT,
            id_association INTEGER,
            FOREIGN KEY (id_association) REFERENCES Association(id_association)
        )''')
        
        db.commit()
        return "Base de données mise à jour avec succès ! (Tables Bureau et Documents créées)"
    except Exception as e:
        return f"Erreur lors de la mise à jour : {str(e)}"

if __name__ == "__main__":
    # Ensure DB is created on first run
    if not os.path.exists(DATABASE):
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

