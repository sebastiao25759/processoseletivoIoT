import machine
import time

# mappeamento dos pinos

LDR_PIN = 35
BUTTON_PIN = 2

"""
valores usados para identificar quando há ou não uma peça no sensor.
quanto mais luz o LDR recebe, menor é o valor lido pelo ADC.
esses valores foram obtidos durante os testes no simulador.
"""

THRESH_FREE = 1200
THRESH_BLOCKED = 1800

# variaveis de tempos

MICROPARADA_MS = 5000
DEBOUNCE_MS = 50
LOOP_DELAY_MS = 20

# inicialização do hardware

adc = machine.ADC(machine.Pin(LDR_PIN))
adc.atten(machine.ADC.ATTN_11DB)
adc.width(machine.ADC.WIDTH_12BIT)

button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

# variáveis de estado

total = 0

blocked = False
blocked_since = None

btn_stable = button.value()
btn_raw_last = btn_stable
btn_last_change_time = time.ticks_ms()

#retorna o tempo atual em milissegundos.
def now_ms():
    return time.ticks_ms()

#Realiza a leitura do sensor LDR.
def read_lux():
    return adc.read()

"""
    processa a leitura do sensor.
    detecta a chegada e saída da peça,
    contabiliza a produção e identifica microparadas.
"""
def handle_sensor(current_time):
    
    global total
    global blocked
    global blocked_since

    lux = read_lux()

    is_blocked = lux > THRESH_BLOCKED
    is_free = lux < THRESH_FREE

    if is_blocked and not blocked:
        blocked = True
        blocked_since = current_time

    if is_free and blocked:
        total += 1
        print("Peca detectada! Total:", total)

        blocked = False
        blocked_since = None

    if blocked and blocked_since is not None:
        if time.ticks_diff(current_time, blocked_since) >= MICROPARADA_MS:
            print("Alerta: Micro-parada detectada!")

            # atualiza o tempo para evitar mensagens repetidas continuamente.
            blocked_since = current_time

"""
    processa o botão utilizando debounce.
    quando o botão é solto, reinicia o turno.
"""
def handle_button(current_time):
    
    global total
    global blocked
    global blocked_since

    global btn_stable
    global btn_raw_last
    global btn_last_change_time

    btn_raw = button.value()

    if btn_raw != btn_raw_last:
        btn_raw_last = btn_raw
        btn_last_change_time = current_time

    if time.ticks_diff(current_time, btn_last_change_time) > DEBOUNCE_MS:

        if btn_raw != btn_stable:
            previous_state = btn_stable
            btn_stable = btn_raw

            if previous_state == 0 and btn_stable == 1:
                total = 0
                blocked = False
                blocked_since = None

                print("Turno resetado com sucesso. Contadores zerados.")

# Programa principal
def main():
    print("Contador de Producao Inicializado")

    while True:
        current_time = now_ms()

        handle_sensor(current_time)
        handle_button(current_time)

        time.sleep_ms(LOOP_DELAY_MS)

if __name__ == "__main__":
    main()