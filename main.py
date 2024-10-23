import psycopg2
from psycopg2.extras import DictCursor
from flask import Flask, make_response, jsonify, request

conn = psycopg2.connect(
    dbname="cps",
    user="postgres",
    password="masterkey",
    host="localhost",
    port="5432"
)

cur = conn.cursor(cursor_factory=DictCursor)
cur.execute("SELECT cod_empresa, codigo, nome, tipo_maquina FROM tmaquina order by codigo desc")

rows = cur.fetchall()
for row in rows: 
    print(row)

cur.close()
#conn.close()    

app = Flask('__name__')
app.config['JSON_SORT_KEYS'] = False
    
@app.route('/maquinas', methods=['GET'])
def get_maquinas():
    return make_response(
        jsonify(
            message='Lista de Maquinas',
            data=rows
        )
    )

@app.route('/maquinas', methods=['POST']) 
def create_maquina():
    machine = request.json
    rows.append(machine)
    cur = conn.cursor()
    cur.execute("INSERT INTO tmaquina (codigo, cod_empresa, nome, tipo_maquina) VALUES (%s, %s, %s,%s)", 
                (machine['codigo'],machine['cod_empresa'], machine['nome'], machine['tipo_maquina']))
    conn.commit()  # É importante fazer o commit para salvar as alterações no banco de dados
    cur.close()
    return make_response(
        jsonify(
            message='Maquina cadastrada com sucesso',
            data=machine
        )
    )

@app.route('/maquinas', methods=['DELETE'])
def del_maquina():
    machine = request.json
    row_encontrada = None

    for row in rows:
        if row['cod_empresa'] == machine['cod_empresa'] and row['codigo'] == machine['codigo']:
            row_encontrada = row
            break

    if row_encontrada:
        rows.remove(row_encontrada)
        cur = conn.cursor()
        cur.execute("DELETE FROM tmaquina WHERE cod_empresa = %s AND codigo = %s", (machine['cod_empresa'], machine['codigo']))
        conn.commit()
        cur.close()
        return make_response(
            jsonify(
                message='Maquina excluída com sucesso',
                data=machine
            )
        )
    else:
        return make_response(
            jsonify(
                message='Nenhuma máquina encontrada para exclusão',
                data=machine
            ),
            404
        )       

app.run()