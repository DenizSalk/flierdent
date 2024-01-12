from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
import sqlite3
import uuid
import json
from datetime import date
import logging

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

logDosyasiAdi = 'gecmis.log'
logging.basicConfig(filename=logDosyasiAdi, level=logging.DEBUG,encoding='utf-8')

def connect_db():
    return sqlite3.connect('data/master.db')

def execute_query(query, parameters=None, fetchone=False):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, parameters) if parameters else cursor.execute(query)
    result = cursor.fetchone() if fetchone else cursor.fetchall()
    conn.commit()
    conn.close()
    return result

def check_user(username, password):
    query = "SELECT * FROM users WHERE username=? AND password=?"
    return execute_query(query, (username, password), fetchone=True)

def get_all_records(search_term=None):
    if search_term:
        query = "SELECT * FROM records_gen WHERE name LIKE ? OR surname LIKE ? OR phone LIKE ? ORDER BY name, surname, phone"
        return execute_query(query, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
    else:
        query = "SELECT * FROM records_gen ORDER BY name, surname, phone, th_id"
        return execute_query(query)

def update_record_gen(th_id, name, surname, birth_date, gender, address, phone, email, tckimlik):
    query = "UPDATE records_gen SET name=?, surname=?, birth_date=?, gender=?, address=?, phone=?, email=?, tckimlik=? WHERE th_id=?"
    execute_query(query, (name, surname, birth_date, gender, address, phone, email, tckimlik, th_id))

def create_record(name, surname, birth_date, gender, address, phone, email, tckimlik, uyruk, kayit, kayitname):
    th_id = str(uuid.uuid4())
    today = date.today()
    query = "INSERT INTO records_gen (th_id, name, surname, birth_date, gender, address, phone, email, tckimlik, uyruk, kayit, kayitname, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    execute_query(query, (th_id, name, surname, birth_date, gender, address, phone, email, tckimlik, uyruk, kayit, kayitname, today))
    logging.info(session['user']+ " kullanıcısı" + name + ""  + surname + " kişisinin kaydını oluşturdu. Girilen Kayıt:" + kayit + kayitname,)
    return th_id

def create_or_update_record_th(th_id, teshis, tedavi, ilac, alerji, sigortabilgi, tarih, tooth, kullanici):
    query = "INSERT INTO records_th (th_id, teshis, tedavi, ilac, alerji, sigortabilgi, tarih, tooth, kullanici) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    execute_query(query, (th_id, teshis, tedavi, ilac, alerji, sigortabilgi, tarih, tooth, kullanici))

def get_events():
    with open('apps.json', 'r') as file:
        data = json.load(file)
    return data['events']

def write_events(events):
    with open('apps.json', 'w') as file:
        json.dump({'events': events}, file, indent=2)

@app.route('/record_edit/<th_id>', methods=['GET', 'POST'])
def record_edit(th_id):
    if 'user' in session:
        if request.method == 'POST':
            data = request.form
            update_record_gen(th_id, **data)
            return redirect(url_for('record_detail', th_id=th_id))
        record_th_data = execute_query("SELECT * FROM records_th WHERE th_id=?", (th_id,), fetchone=False)
        record = execute_query("SELECT * FROM records_gen WHERE th_id=?", (th_id,), fetchone=True)
        return render_template('record_edit.html', record=record, record_th_data=record_th_data)
    else:
        return render_template('login.html')

@app.route('/')
def home():
    if 'user' in session:
        username = session['user']
        with open('apps.json', 'r') as file:
            apodata = json.load(file)
        records_gen_count = execute_query("SELECT COUNT(*) FROM records_gen")[0]
        records_th_count = execute_query("SELECT COUNT(*) FROM records_th")[0]
        return render_template('dashboard.html', apodata=apodata, records_gen_count=records_gen_count, records_th_count=records_th_count)
    else:
        return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = check_user(username, password)

        if user:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            return "Kullanıcı adı veya şifre yanlış. Lütfen tekrar deneyin."

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/kayit_olustur', methods=['POST', 'GET'])
def record_create():
    if 'user' in session:
        if request.method == 'POST':
            name = request.form['name']
            surname = request.form['surname']
            birth_date = request.form['birth_date']
            gender = request.form['gender']
            address = request.form['address']
            phone = request.form['phone']
            email = request.form['email']
            tckimlik = request.form['tckimlik']
            uyruk = request.form['uyruk']
            kayit = request.form['kayit']
            kayitname = request.form['kayitname']

            th_id = create_record(name, surname, birth_date, gender, address, phone, email, tckimlik, uyruk, kayit, kayitname)

            return redirect(url_for('record_detail', th_id=th_id, create=True, name=name, surname=surname))

        return render_template('record_create.html')
    else:
        return render_template('login.html')
    
@app.route('/randevu', methods=['POST', 'GET'])
def randevu():
    search_term = request.args.get('search', '')
    records = get_all_records(search_term)
    with open('apps.json', 'r') as file:
        apodata = json.load(file)
    if 'user' in session:
        return render_template('randevu.html', records=records, search_term=search_term, apodata=apodata)
    else:
        return render_template('login.html')

@app.route('/add_event', methods=['POST'])
def add_event():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        saat = request.form['saat']
        day = request.form['day']
        month = request.form['month']
        year = request.form['year']
        match month:
            case "Ock":
                month = 1
            case "Şbt":
                month = 2
            case "Mar":
                month = 3
            case "Nis":
                month = 4
            case "May":
                month = 5
            case "Haz":
                month = 6
            case "Tem":
                month = 7
            case "Agt":
                month = 8
            case "Eyl":
                month = 9
            case "Ekm":
                month = 10
            case "Ksm":
                month = 11
            case "Arl":
                month = 12
        # Load existing data from apps.json
        with open('apps.json', 'r') as json_file:
            data = json.load(json_file)

        # Add new event to the data
        new_event = {
            'name': name.split(';')[0],
            'saat': saat,
            'day': int(day),
            'month': int(month),
            'year': int(year),
            'cancelled': False,  # You may set this based on your requirements
            'th_id': str(name.split(';')[1])
        }

        data['events'].append(new_event)

        # Write updated data back to apps.json
        with open('apps.json', 'w') as json_file:
            json.dump(data, json_file, indent=2)

        return redirect("/randevu")

@app.route('/event_edit', methods=['GET'])
def event_edit():
    action = request.args.get('action')
    print(type(action))
    th_id = request.args.get('th_id')
    print(type(th_id))
    day = int(request.args.get('day'))
    print(type(day))
    saat = request.args.get('saat')
    print(type(saat))
    month = int(request.args.get('month'))
    print(type(month))
    year = int(request.args.get('year'))
    print(type(year))
    with open('apps.json', 'r') as file:
        data = json.load(file)
    events = data.get('events', [])
    if action == 'cancel':
        for event in events:
            if (
                event['th_id'] == th_id and
                event['day'] == day and
                event['saat'] == saat and
                event['month'] == month and
                event['year'] == year
            ):
                event['cancelled'] = True
    elif action == 'delete':
        events = [
            event for event in events if not (
                event['th_id'] == th_id and
                event['day'] == day and
                event['saat'] == saat and
                event['month'] == month and
                event['year'] == year
            )
        ]
    data['events'] = events
    with open('apps.json', 'w') as file:
        json.dump(data, file, indent=2)
    return redirect(url_for('randevu'))

@app.route('/record_detail', methods=['GET', 'POST'])
def record_detail():
    th_id = request.args.get('th_id')
    name = request.args.get('name')
    surname = request.args.get('surname')
    return render_template('record_detail.html', th_id=th_id, name=name, surname=surname)

@app.route('/record_detail_create', methods=['GET', 'POST'])
def record_detail_create():
    if request.method == 'POST':
        th_id = request.form['th_id']
        teshis = request.form['teshis']
        tedavi = request.form['tedavi']
        ilac = request.form['ilac']
        alerji = request.form['alerji']
        sigortabilgi = request.form['sigortabilgi']
        tarih = request.form['tarih']
        kullanici = request.form['kullanici']
        print(kullanici)
        toothlist = []
        for i in range(1,32):
            try:
                print(i)
                currenttooth = "tooth"+str(i)
                print(currenttooth)
                if request.form[currenttooth]:
                    print(currenttooth)
                    tooth = currenttooth + " : " + request.form[currenttooth]
                    print(tooth)
                    toothlist.append(tooth)
                print(toothlist)
            except:
                print("diş hatası")
        try:
            toothlist_string = ', '.join(toothlist)
        except:
            toothlist_string = ""
        
        create_or_update_record_th(th_id, teshis, tedavi, ilac, alerji, sigortabilgi, tarih, toothlist_string, kullanici)

    return redirect(url_for('record_detail', th_id=th_id))

@app.route('/record_search')
def record_search():
    if 'user' in session:
        search_term = request.args.get('search', '')
        records = get_all_records(search_term)
        return render_template('record_search.html', records=records, search_term=search_term)
    else:
        return render_template('login.html')
    
@app.route('/search_record_detail', methods=['GET'])
def search_record_detail():
    if 'user' in session:
        # Retrieve th_id from the query parameters
        th_id = request.args.get('th_id')

        # Retrieve data from records_th table for the given th_id
        record_th_data = execute_query("SELECT * FROM records_th WHERE th_id=?", (th_id,), fetchone=False)

        if record_th_data:
            # Render template with the retrieved data
            return render_template('search_record_detail.html', record_th_data=record_th_data)
        else:
            # Handle the case where no data is found for the given th_id
            return render_template('record_th_not_found.html', th_id=th_id)
    else:
        # Redirect to login page if the user is not logged in
        return render_template('login.html')

def load_data():
    try:
        with open('ted.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {"events": []}
    return data['events']

# Veriyi JSON dosyasına yaz
def save_data(events):
    with open('ted.json', 'w') as file:
        json.dump({"events": events}, file, indent=4)

# Ana sayfa
@app.route('/hizmetler', methods=['GET', 'POST'])
def hizmetler():
    if request.method == 'POST':
        if request.form['action'] == 'create':
            return create_event()
        elif request.form['action'] == 'edit':
            return edit_event_form(request.form['event_id'])
        elif request.form['action'] == 'update':
            return update_event(request.form['event_id'])
        elif request.form['action'] == 'delete':
            return delete_event(request.form['event_id'])

    events = load_data()
    return render_template('hizmetler.html', events=events)

# Yeni bir etkinlik oluştur
def create_event():
    events = load_data()
    data = request.form.to_dict()
    new_event = {
        'id': len(events) + 1,
        'name': data['name'],
        'price': float(data['price']),
        'aciklama': data['aciklama']
    }
    events.append(new_event)
    save_data(events)
    return render_template('hizmetler.html', events=events)

# Belirli bir etkinliği düzenle formu
def edit_event_form(event_id):
    events = load_data()
    event = next((event for event in events if event['id'] == int(event_id)), None)
    if event is None:
        return jsonify({'error': 'Etkinlik bulunamadı'}), 404
    return render_template('hizmetler.html', events=events, edit_event=event)

# Belirli bir etkinliği güncelle
def update_event(event_id):
    events = load_data()
    event = next((event for event in events if event['id'] == int(event_id)), None)
    if event is None:
        return jsonify({'error': 'Etkinlik bulunamadı'}), 404

    data = request.form.to_dict()
    event['name'] = data['name']
    event['price'] = float(data['price'])
    event['aciklama'] = data['aciklama']

    save_data(events)
    return render_template('hizmetler.html', events=events)

# Belirli bir etkinliği sil
def delete_event(event_id):
    events = load_data()
    events = [event for event in events if event['id'] != int(event_id)]
    save_data(events)
    return render_template('hizmetler.html', events=events)


if __name__ == '__main__':
    app.run(debug=True)