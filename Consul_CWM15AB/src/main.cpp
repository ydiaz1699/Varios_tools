// ============================================
// Consul CWH15AB - ESP32 Controller
// Replica la logica de lavado de fabrica
// 16 programas + encoder rotativo + display
// ============================================
//
// Autor: ydiaz1699
// Fecha: 2026
// Modelo base: Consul CWH15AB (15kg, 16 programas)
// Panel: Display Digital + Boton giratorio (encoder)
// ============================================

#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

// ─── DISPLAY LCD I2C (16x2) ─────────────────────────────
// Usa LCD 16x2 con modulo I2C para replicar display digital
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ─── PINES DE SALIDA (ACTUADORES) ────────────────────────
#define PIN_VALVULA_AGUA    25   // Solenoide entrada de agua
#define PIN_MOTOR_DIR_A     26   // Motor agitacion sentido A
#define PIN_MOTOR_DIR_B     27   // Motor agitacion sentido B
#define PIN_CENTRIFUGADO    32   // Motor centrifugado
#define PIN_BOMBA_DRENAJE   33   // Bomba de drenaje
#define PIN_TRAVA_TAPA      14   // Electroiman trava de tapa

// ─── PINES DE ENTRADA (SENSORES) ─────────────────────────
#define PIN_PRESOSTATO_BAJO  34  // Nivel bajo (activo LOW)
#define PIN_PRESOSTATO_ALTO  35  // Nivel alto (activo LOW)
#define PIN_TAPA_CERRADA     36  // Microswitch tapa (activo LOW)

// ─── ENCODER ROTATIVO (selector de programa) ─────────────
#define PIN_ENCODER_CLK      18  // Clock del encoder
#define PIN_ENCODER_DT       19  // Data del encoder
#define PIN_ENCODER_SW       21  // Boton push del encoder

// ─── BOTONES DEL PANEL ───────────────────────────────────
#define PIN_BTN_POWER         4  // Encender/Apagar
#define PIN_BTN_INICIO        5  // Iniciar/Pausar ciclo
#define PIN_BTN_NIVEL        16  // Seleccionar nivel de agua
#define PIN_BTN_MAIS_SECAS   17  // Funcion Mais Secas (extra spin)

// ─── LED INDICADOR ───────────────────────────────────────
#define PIN_LED_STATUS       23  // LED de estado general


// ─── CONSTANTES DE SEGURIDAD ─────────────────────────────
#define TIMEOUT_LLENADO_MS   900000   // 15 min max para llenar
#define TIEMPO_DRENAJE_MS    90000    // 90 seg para drenar
#define DEBOUNCE_MS          200      // Debounce botones
#define ENCODER_DEBOUNCE_MS  5        // Debounce encoder

// ─── ESTADOS DE LA MAQUINA ───────────────────────────────
enum EstadoMaquina {
  APAGADA,
  IDLE,
  MOLHO,              // Remojo (solo llena y deja en reposo)
  LLENADO,
  LAVADO,
  DRENAJE_LAVADO,
  LLENADO_ENJUAGUE,
  ENJUAGUE,
  DRENAJE_ENJUAGUE,
  CENTRIFUGADO,
  CENTRIFUGADO_EXTRA, // Mais Secas
  FINALIZADO,
  ERROR_TIMEOUT
};

// ─── 16 PROGRAMAS DE LAVADO (CWH15AB) ───────────────────
enum Programa {
  PROG_BRANCAS = 0,       // 1. Roupas Brancas
  PROG_COLORIDAS,         // 2. Roupas Coloridas
  PROG_ESCURAS,           // 3. Roupas Escuras
  PROG_JEANS,             // 4. Jeans
  PROG_CAMA_BANHO,        // 5. Cama e Banho
  PROG_DELICADAS,         // 6. Roupas Delicadas
  PROG_BEBE,             // 7. Roupas de Bebe
  PROG_CASACOS,           // 8. Casacos e Moletons
  PROG_TENIS,             // 9. Tenis
  PROG_PESADAS,           // 10. Roupas Pesadas
  PROG_EDREDOM,           // 11. Edredom
  PROG_TIRA_ODORES,       // 12. Tira Odores
  PROG_RAPIDO,            // 13. Ciclo Rapido
  PROG_ENXAGUE,           // 14. Enxague (solo enjuague)
  PROG_CENTRIFUGACAO,     // 15. Centrifugacao (solo centrif.)
  PROG_MOLHO,             // 16. Molho (remojo)
  NUM_PROGRAMAS
};


// Nombres para display (max 16 chars)
const char* nombrePrograma[NUM_PROGRAMAS] = {
  "Brancas",
  "Coloridas",
  "Escuras",
  "Jeans",
  "Cama e Banho",
  "Delicadas",
  "Roupas Bebe",
  "Casacos",
  "Tenis",
  "Pesadas",
  "Edredom",
  "Tira Odores",
  "Rapido",
  "Enxague",
  "Centrifugacao",
  "Molho"
};

// ─── NIVELES DE AGUA ─────────────────────────────────────
enum NivelAgua {
  NIVEL_BAIXO = 0,    // Bajo
  NIVEL_MEDIO,        // Medio
  NIVEL_ALTO,         // Alto
  NIVEL_EXTRA,        // Extra alto
  NUM_NIVELES
};

const char* nombreNivel[NUM_NIVELES] = {
  "Baixo", "Medio", "Alto", "Extra"
};


// ─── PARAMETROS DE CADA CICLO ────────────────────────────
// IMPORTANTE: Ajustar estos valores con cronometro midiendo
//             la placa original ANTES de reemplazarla.
struct ParametrosCiclo {
  unsigned long tiempoLavado;       // Tiempo agitacion total (ms)
  unsigned long tiempoAgitacion;    // Duracion en una direccion (ms)
  unsigned long pausaAgitacion;     // Pausa entre cambios dir (ms)
  int           numEnjuagues;       // Cantidad de enjuagues
  unsigned long tiempoEnjuague;     // Duracion cada enjuague (ms)
  unsigned long tiempoCentrifugado; // Centrifugado final (ms)
  bool          agitacionFuerte;    // true = fuerte, false = suave
  NivelAgua     nivelDefault;       // Nivel de agua por defecto
};

// Tabla de 16 ciclos - AJUSTAR CON MEDICIONES REALES
const ParametrosCiclo ciclos[NUM_PROGRAMAS] = {
  // 1. BRANCAS: lavado intenso, 2 enjuagues, centrif largo
  { 840000, 4000, 2000, 2, 240000, 420000, true,  NIVEL_ALTO },
  // 2. COLORIDAS: lavado normal, 2 enjuagues
  { 720000, 4000, 2000, 2, 180000, 360000, true,  NIVEL_ALTO },
  // 3. ESCURAS: lavado suave, 2 enjuagues, centrif corto
  { 600000, 3000, 3000, 2, 180000, 300000, false, NIVEL_ALTO },
  // 4. JEANS: lavado fuerte, 2 enjuagues
  { 780000, 4000, 2000, 2, 240000, 420000, true,  NIVEL_ALTO },
  // 5. CAMA E BANHO: lavado largo, 2 enjuagues, centrif largo
  { 900000, 4000, 2000, 2, 240000, 480000, true,  NIVEL_EXTRA },
  // 6. DELICADAS: lavado suave corto, 1 enjuague, centrif corto
  { 420000, 3000, 4000, 1, 180000, 180000, false, NIVEL_MEDIO },
  // 7. BEBE: lavado largo suave, 3 enjuagues (extra enjuague)
  { 720000, 3000, 3000, 3, 240000, 360000, false, NIVEL_ALTO },
  // 8. CASACOS: lavado fuerte largo, 2 enjuagues
  { 840000, 4000, 2000, 2, 240000, 420000, true,  NIVEL_EXTRA },
  // 9. TENIS: lavado suave, 1 enjuague, centrif corto
  { 600000, 3000, 4000, 1, 180000, 240000, false, NIVEL_MEDIO },
  // 10. PESADAS: lavado intenso largo, 2 enjuagues, centrif max
  { 900000, 4000, 2000, 2, 240000, 480000, true,  NIVEL_EXTRA },
  // 11. EDREDOM: lavado suave muy largo, 2 enjuagues, centrif suave
  { 1020000, 3000, 5000, 2, 300000, 360000, false, NIVEL_EXTRA },
  // 12. TIRA ODORES: lavado largo, 3 enjuagues
  { 780000, 4000, 2000, 3, 240000, 360000, true,  NIVEL_ALTO },
  // 13. RAPIDO: lavado corto, 1 enjuague, centrif corto
  { 300000, 3000, 2000, 1, 120000, 180000, true,  NIVEL_BAIXO },
  // 14. ENXAGUE: sin lavado, 2 enjuagues, centrif normal
  { 0, 0, 0, 2, 180000, 300000, true,  NIVEL_MEDIO },
  // 15. CENTRIFUGACAO: solo centrifugado
  { 0, 0, 0, 0, 0, 480000, true,  NIVEL_BAIXO },
  // 16. MOLHO: solo llena y deja en reposo (30 min)
  { 1800000, 0, 0, 0, 0, 0, false, NIVEL_ALTO },
};


// ─── VARIABLES GLOBALES ──────────────────────────────────
EstadoMaquina estadoActual = APAGADA;
Programa programaSeleccionado = PROG_COLORIDAS;
NivelAgua nivelSeleccionado = NIVEL_ALTO;
bool maisSeca = false;          // Funcion "Mais Secas" activada
int enjuagueActual = 0;
unsigned long tiempoInicioEtapa = 0;
bool direccionMotor = false;
unsigned long ultimoCambioDir = 0;
unsigned long ultimoDebounce = 0;

// Encoder
volatile int encoderPos = 1;    // Posicion encoder (0-15)
int lastEncoderPos = 1;
volatile unsigned long lastEncoderTime = 0;
int lastCLK = HIGH;

// Display
unsigned long ultimoUpdateDisplay = 0;
#define DISPLAY_UPDATE_MS 250

// ─── FUNCIONES DE ACTUADORES ─────────────────────────────

void apagarTodo() {
  digitalWrite(PIN_VALVULA_AGUA, LOW);
  digitalWrite(PIN_MOTOR_DIR_A, LOW);
  digitalWrite(PIN_MOTOR_DIR_B, LOW);
  digitalWrite(PIN_CENTRIFUGADO, LOW);
  digitalWrite(PIN_BOMBA_DRENAJE, LOW);
}

void abrirAgua() { digitalWrite(PIN_VALVULA_AGUA, HIGH); }
void cerrarAgua() { digitalWrite(PIN_VALVULA_AGUA, LOW); }

void agitar(bool dir) {
  if (dir) {
    digitalWrite(PIN_MOTOR_DIR_A, HIGH);
    digitalWrite(PIN_MOTOR_DIR_B, LOW);
  } else {
    digitalWrite(PIN_MOTOR_DIR_A, LOW);
    digitalWrite(PIN_MOTOR_DIR_B, HIGH);
  }
}

void pararAgitacion() {
  digitalWrite(PIN_MOTOR_DIR_A, LOW);
  digitalWrite(PIN_MOTOR_DIR_B, LOW);
}

void iniciarCentrifugado() { digitalWrite(PIN_CENTRIFUGADO, HIGH); }
void pararCentrifugado() { digitalWrite(PIN_CENTRIFUGADO, LOW); }
void iniciarDrenaje() { digitalWrite(PIN_BOMBA_DRENAJE, HIGH); }
void pararDrenaje() { digitalWrite(PIN_BOMBA_DRENAJE, LOW); }
void travarTapa() { digitalWrite(PIN_TRAVA_TAPA, HIGH); }
void destravarTapa() { digitalWrite(PIN_TRAVA_TAPA, LOW); }


// ─── FUNCIONES DE SENSORES ───────────────────────────────

bool nivelAlcanzado() {
  switch (nivelSeleccionado) {
    case NIVEL_BAIXO:
    case NIVEL_MEDIO:
      return digitalRead(PIN_PRESOSTATO_BAJO) == LOW;
    case NIVEL_ALTO:
    case NIVEL_EXTRA:
      return digitalRead(PIN_PRESOSTATO_ALTO) == LOW;
    default:
      return digitalRead(PIN_PRESOSTATO_BAJO) == LOW;
  }
}

bool tapaCerrada() {
  return digitalRead(PIN_TAPA_CERRADA) == LOW;
}

// ─── ENCODER ROTATIVO ────────────────────────────────────

void IRAM_ATTR encoderISR() {
  if (millis() - lastEncoderTime < ENCODER_DEBOUNCE_MS) return;
  lastEncoderTime = millis();

  int clk = digitalRead(PIN_ENCODER_CLK);
  int dt = digitalRead(PIN_ENCODER_DT);

  if (clk != lastCLK && clk == LOW) {
    if (dt != clk) {
      encoderPos++;
      if (encoderPos >= NUM_PROGRAMAS) encoderPos = 0;
    } else {
      encoderPos--;
      if (encoderPos < 0) encoderPos = NUM_PROGRAMAS - 1;
    }
  }
  lastCLK = clk;
}


// ─── DISPLAY LCD ─────────────────────────────────────────

void mostrarProgramaSeleccionado() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(nombrePrograma[programaSeleccionado]);
  lcd.setCursor(0, 1);
  lcd.print("Niv:");
  lcd.print(nombreNivel[nivelSeleccionado]);
  if (maisSeca) {
    lcd.setCursor(11, 1);
    lcd.print("+SEC");
  }
}

void mostrarEstado() {
  if (millis() - ultimoUpdateDisplay < DISPLAY_UPDATE_MS) return;
  ultimoUpdateDisplay = millis();

  lcd.setCursor(0, 0);
  unsigned long tiempoEnEtapa = millis() - tiempoInicioEtapa;
  unsigned long tiempoRestante = 0;
  const ParametrosCiclo &p = ciclos[programaSeleccionado];

  switch (estadoActual) {
    case LLENADO:
    case LLENADO_ENJUAGUE:
      lcd.clear();
      lcd.print("Enchendo...");
      lcd.setCursor(0, 1);
      lcd.print(nombrePrograma[programaSeleccionado]);
      break;
    case LAVADO:
      lcd.clear();
      lcd.print("Lavando");
      tiempoRestante = (p.tiempoLavado > tiempoEnEtapa) ?
        (p.tiempoLavado - tiempoEnEtapa) / 60000 : 0;
      lcd.setCursor(0, 1);
      lcd.print(tiempoRestante);
      lcd.print(" min restam");
      break;
    case MOLHO:
      lcd.clear();
      lcd.print("Molho");
      tiempoRestante = (p.tiempoLavado > tiempoEnEtapa) ?
        (p.tiempoLavado - tiempoEnEtapa) / 60000 : 0;
      lcd.setCursor(0, 1);
      lcd.print(tiempoRestante);
      lcd.print(" min restam");
      break;
    case ENJUAGUE:
      lcd.clear();
      lcd.print("Enxaguando");
      lcd.setCursor(0, 1);
      lcd.print(enjuagueActual + 1);
      lcd.print("/");
      lcd.print(p.numEnjuagues);
      break;
    case DRENAJE_LAVADO:
    case DRENAJE_ENJUAGUE:
      lcd.clear();
      lcd.print("Drenando...");
      break;
    case CENTRIFUGADO:
    case CENTRIFUGADO_EXTRA:
      lcd.clear();
      lcd.print("Centrifugando");
      tiempoRestante = (p.tiempoCentrifugado > tiempoEnEtapa) ?
        (p.tiempoCentrifugado - tiempoEnEtapa) / 60000 : 0;
      lcd.setCursor(0, 1);
      lcd.print(tiempoRestante);
      lcd.print(" min restam");
      break;
    case FINALIZADO:
      lcd.clear();
      lcd.print("** PRONTO! **");
      lcd.setCursor(0, 1);
      lcd.print("Retire as roupas");
      break;
    case ERROR_TIMEOUT:
      lcd.clear();
      lcd.print("!! ERRO !!");
      lcd.setCursor(0, 1);
      lcd.print("Timeout enchim.");
      break;
    default:
      break;
  }
}


// ─── MAQUINA DE ESTADOS PRINCIPAL ────────────────────────

void ejecutarCiclo() {
  const ParametrosCiclo &params = ciclos[programaSeleccionado];
  unsigned long tiempoEnEtapa = millis() - tiempoInicioEtapa;

  switch (estadoActual) {

    // ── MOLHO (REMOJO) ───────────────────────────────────
    case MOLHO:
      // Solo deja el agua quieta por el tiempo configurado
      if (tiempoEnEtapa >= params.tiempoLavado) {
        // Fin del remojo, drenar
        iniciarDrenaje();
        estadoActual = DRENAJE_LAVADO;
        tiempoInicioEtapa = millis();
        Serial.println("Molho finalizado -> Drenaje");
      }
      break;

    // ── LLENADO ──────────────────────────────────────────
    case LLENADO:
      abrirAgua();
      if (nivelAlcanzado()) {
        cerrarAgua();
        // Programa MOLHO: solo remojo, no agita
        if (programaSeleccionado == PROG_MOLHO) {
          estadoActual = MOLHO;
        } else if (params.tiempoLavado > 0) {
          estadoActual = LAVADO;
          ultimoCambioDir = millis();
        } else if (params.numEnjuagues > 0) {
          estadoActual = ENJUAGUE;
          enjuagueActual = 0;
          ultimoCambioDir = millis();
        } else {
          estadoActual = CENTRIFUGADO;
        }
        tiempoInicioEtapa = millis();
      }
      if (tiempoEnEtapa > TIMEOUT_LLENADO_MS) {
        cerrarAgua();
        apagarTodo();
        destravarTapa();
        estadoActual = ERROR_TIMEOUT;
        Serial.println("ERROR: Timeout llenado!");
      }
      break;

    // ── LAVADO (AGITACION) ───────────────────────────────
    case LAVADO: {
      unsigned long cicloAgit = params.tiempoAgitacion + params.pausaAgitacion;

      if (millis() - ultimoCambioDir >= cicloAgit) {
        direccionMotor = !direccionMotor;
        ultimoCambioDir = millis();
      }

      if (millis() - ultimoCambioDir < params.tiempoAgitacion) {
        agitar(direccionMotor);
      } else {
        pararAgitacion();
      }

      if (tiempoEnEtapa >= params.tiempoLavado) {
        pararAgitacion();
        iniciarDrenaje();
        estadoActual = DRENAJE_LAVADO;
        tiempoInicioEtapa = millis();
        Serial.println("Lavado -> Drenaje");
      }
      break;
    }


    // ── DRENAJE POST-LAVADO ──────────────────────────────
    case DRENAJE_LAVADO:
      if (tiempoEnEtapa >= TIEMPO_DRENAJE_MS) {
        pararDrenaje();
        if (params.numEnjuagues > 0) {
          enjuagueActual = 0;
          estadoActual = LLENADO_ENJUAGUE;
        } else if (params.tiempoCentrifugado > 0) {
          estadoActual = CENTRIFUGADO;
        } else {
          estadoActual = FINALIZADO;
          destravarTapa();
        }
        tiempoInicioEtapa = millis();
      }
      break;

    // ── LLENADO PARA ENJUAGUE ────────────────────────────
    case LLENADO_ENJUAGUE:
      abrirAgua();
      if (nivelAlcanzado()) {
        cerrarAgua();
        estadoActual = ENJUAGUE;
        tiempoInicioEtapa = millis();
        ultimoCambioDir = millis();
        Serial.printf("Enxague %d/%d\n",
                      enjuagueActual + 1, params.numEnjuagues);
      }
      if (tiempoEnEtapa > TIMEOUT_LLENADO_MS) {
        cerrarAgua();
        apagarTodo();
        destravarTapa();
        estadoActual = ERROR_TIMEOUT;
      }
      break;

    // ── ENJUAGUE ─────────────────────────────────────────
    case ENJUAGUE: {
      // Agitacion suave: 3s cada dir, 3s pausa
      unsigned long cicloEnj = 6000;
      if (millis() - ultimoCambioDir >= cicloEnj) {
        direccionMotor = !direccionMotor;
        ultimoCambioDir = millis();
      }
      if (millis() - ultimoCambioDir < 3000) {
        agitar(direccionMotor);
      } else {
        pararAgitacion();
      }

      if (tiempoEnEtapa >= params.tiempoEnjuague) {
        pararAgitacion();
        iniciarDrenaje();
        estadoActual = DRENAJE_ENJUAGUE;
        tiempoInicioEtapa = millis();
      }
      break;
    }

    // ── DRENAJE POST-ENJUAGUE ────────────────────────────
    case DRENAJE_ENJUAGUE:
      if (tiempoEnEtapa >= TIEMPO_DRENAJE_MS) {
        pararDrenaje();
        enjuagueActual++;
        if (enjuagueActual < params.numEnjuagues) {
          estadoActual = LLENADO_ENJUAGUE;
        } else if (params.tiempoCentrifugado > 0) {
          estadoActual = CENTRIFUGADO;
        } else {
          estadoActual = FINALIZADO;
          destravarTapa();
        }
        tiempoInicioEtapa = millis();
      }
      break;


    // ── CENTRIFUGADO ─────────────────────────────────────
    case CENTRIFUGADO:
      iniciarDrenaje();
      iniciarCentrifugado();

      // Seguridad: tapa abierta
      if (!tapaCerrada()) {
        pararCentrifugado();
        pararDrenaje();
        Serial.println("ALERTA: Tapa abierta!");
        break;
      }

      if (tiempoEnEtapa >= params.tiempoCentrifugado) {
        pararCentrifugado();
        pararDrenaje();
        // Si "Mais Secas" esta activado, hacer centrifugado extra
        if (maisSeca) {
          estadoActual = CENTRIFUGADO_EXTRA;
          tiempoInicioEtapa = millis();
          Serial.println("Centrifugado extra (Mais Secas)");
        } else {
          destravarTapa();
          estadoActual = FINALIZADO;
          Serial.println("=== CICLO PRONTO ===");
        }
      }
      break;

    // ── CENTRIFUGADO EXTRA (MAIS SECAS) ──────────────────
    case CENTRIFUGADO_EXTRA:
      iniciarDrenaje();
      iniciarCentrifugado();

      if (!tapaCerrada()) {
        pararCentrifugado();
        pararDrenaje();
        break;
      }

      // 5 minutos extra de centrifugado
      if (tiempoEnEtapa >= 300000) {
        pararCentrifugado();
        pararDrenaje();
        destravarTapa();
        estadoActual = FINALIZADO;
        Serial.println("=== CICLO PRONTO ===");
      }
      break;

    // ── FINALIZADO ───────────────────────────────────────
    case FINALIZADO:
      apagarTodo();
      destravarTapa();
      break;

    // ── ERROR ────────────────────────────────────────────
    case ERROR_TIMEOUT:
      apagarTodo();
      destravarTapa();
      break;

    default:
      break;
  }
}


// ─── MANEJO DE BOTONES ───────────────────────────────────

void leerBotones() {
  if (millis() - ultimoDebounce < DEBOUNCE_MS) return;

  // ── BOTON POWER ──
  if (digitalRead(PIN_BTN_POWER) == LOW) {
    ultimoDebounce = millis();
    if (estadoActual == APAGADA) {
      estadoActual = IDLE;
      programaSeleccionado = PROG_COLORIDAS;
      nivelSeleccionado = NIVEL_ALTO;
      maisSeca = false;
      encoderPos = PROG_COLORIDAS;
      lcd.backlight();
      mostrarProgramaSeleccionado();
      Serial.println("Ligada - IDLE");
    } else {
      apagarTodo();
      destravarTapa();
      estadoActual = APAGADA;
      lcd.noBacklight();
      lcd.clear();
      Serial.println("Desligada");
    }
    return;
  }

  // Solo en IDLE
  if (estadoActual != IDLE) return;

  // ── BOTON NIVEL AGUA ──
  if (digitalRead(PIN_BTN_NIVEL) == LOW) {
    ultimoDebounce = millis();
    nivelSeleccionado = (NivelAgua)((nivelSeleccionado + 1) % NUM_NIVELES);
    mostrarProgramaSeleccionado();
    Serial.printf("Nivel: %s\n", nombreNivel[nivelSeleccionado]);
  }

  // ── BOTON MAIS SECAS ──
  if (digitalRead(PIN_BTN_MAIS_SECAS) == LOW) {
    ultimoDebounce = millis();
    maisSeca = !maisSeca;
    mostrarProgramaSeleccionado();
    Serial.printf("Mais Secas: %s\n", maisSeca ? "ON" : "OFF");
  }

  // ── BOTON INICIO ──
  if (digitalRead(PIN_BTN_INICIO) == LOW) {
    ultimoDebounce = millis();

    if (!tapaCerrada()) {
      Serial.println("Tampa aberta! Nao inicia.");
      lcd.clear();
      lcd.print("Feche a tampa!");
      delay(2000);
      mostrarProgramaSeleccionado();
      return;
    }

    // Iniciar ciclo
    travarTapa();
    enjuagueActual = 0;
    tiempoInicioEtapa = millis();
    ultimoCambioDir = millis();
    direccionMotor = false;

    const ParametrosCiclo &params = ciclos[programaSeleccionado];

    // Determinar estado inicial segun programa
    if (programaSeleccionado == PROG_CENTRIFUGACAO) {
      estadoActual = CENTRIFUGADO;
      Serial.println("=== INICIO: Centrifugacao ===");
    } else if (programaSeleccionado == PROG_ENXAGUE) {
      estadoActual = LLENADO_ENJUAGUE;
      Serial.println("=== INICIO: Enxague ===");
    } else {
      estadoActual = LLENADO;
      Serial.println("=== INICIO: Enchendo ===");
    }
  }
}


// ─── LEER ENCODER ────────────────────────────────────────

void leerEncoder() {
  if (estadoActual != IDLE) return;

  if (encoderPos != lastEncoderPos) {
    lastEncoderPos = encoderPos;
    programaSeleccionado = (Programa)encoderPos;
    // Ajustar nivel default del programa
    nivelSeleccionado = ciclos[programaSeleccionado].nivelDefault;
    mostrarProgramaSeleccionado();
    Serial.printf("Programa: %s\n",
                  nombrePrograma[programaSeleccionado]);
  }
}

// ─── SETUP ───────────────────────────────────────────────

void setup() {
  Serial.begin(115200);
  Serial.println("\n====================================");
  Serial.println("  Consul CWH15AB - ESP32 Controller");
  Serial.println("  16 Programas - Panel Digital");
  Serial.println("====================================\n");

  // Configurar pines de salida
  const int pinesSalida[] = {
    PIN_VALVULA_AGUA, PIN_MOTOR_DIR_A, PIN_MOTOR_DIR_B,
    PIN_CENTRIFUGADO, PIN_BOMBA_DRENAJE, PIN_TRAVA_TAPA,
    PIN_LED_STATUS
  };
  for (int pin : pinesSalida) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }

  // Configurar pines de entrada
  const int pinesEntrada[] = {
    PIN_PRESOSTATO_BAJO, PIN_PRESOSTATO_ALTO,
    PIN_TAPA_CERRADA, PIN_BTN_POWER, PIN_BTN_INICIO,
    PIN_BTN_NIVEL, PIN_BTN_MAIS_SECAS, PIN_ENCODER_SW
  };
  for (int pin : pinesEntrada) {
    pinMode(pin, INPUT_PULLUP);
  }

  // Encoder rotativo
  pinMode(PIN_ENCODER_CLK, INPUT_PULLUP);
  pinMode(PIN_ENCODER_DT, INPUT_PULLUP);
  lastCLK = digitalRead(PIN_ENCODER_CLK);
  attachInterrupt(digitalPinToInterrupt(PIN_ENCODER_CLK),
                  encoderISR, CHANGE);

  // Inicializar LCD
  lcd.init();
  lcd.noBacklight();  // Apagado hasta que enciendan

  estadoActual = APAGADA;
  Serial.println("Sistema pronto. Pressione POWER.");
}

// ─── LOOP PRINCIPAL ──────────────────────────────────────

void loop() {
  leerBotones();
  leerEncoder();

  if (estadoActual != APAGADA && estadoActual != IDLE) {
    ejecutarCiclo();
    mostrarEstado();

    // LED status parpadea durante operacion
    digitalWrite(PIN_LED_STATUS, (millis() / 1000) % 2);
  }

  // LED status fijo en FINALIZADO
  if (estadoActual == FINALIZADO) {
    digitalWrite(PIN_LED_STATUS, (millis() / 300) % 2);
  }

  delay(10);
}
