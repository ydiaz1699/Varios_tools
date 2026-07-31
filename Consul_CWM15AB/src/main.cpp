// ============================================
// Consul CWM15AB - ESP32 Controller
// Replica la logica de lavado de fabrica
// ============================================
//
// Autor: ydiaz1699
// Fecha: 2026
// Descripcion: Firmware para reemplazar la placa original
//              de la lavadora Consul CWM15AB con ESP32,
//              manteniendo panel de botones/LEDs y ciclos originales.
// ============================================

#include <Arduino.h>

// ─── PINES DE SALIDA (ACTUADORES) ────────────────────────
#define PIN_VALVULA_AGUA    25   // Solenoide entrada de agua
#define PIN_MOTOR_DIR_A     26   // Motor agitacion sentido A
#define PIN_MOTOR_DIR_B     27   // Motor agitacion sentido B
#define PIN_CENTRIFUGADO    32   // Motor centrifugado
#define PIN_BOMBA_DRENAJE   33   // Bomba de drenaje
#define PIN_TRAVA_TAPA      14   // Electroiman trava de tapa

// ─── PINES DE ENTRADA (SENSORES) ─────────────────────────
#define PIN_PRESOSTATO_BAJO  34  // Nivel bajo alcanzado (activo LOW)
#define PIN_PRESOSTATO_ALTO  35  // Nivel alto alcanzado (activo LOW)
#define PIN_TAPA_CERRADA     36  // Microswitch tapa (activo LOW)

// ─── PINES DEL PANEL DE USUARIO ──────────────────────────
// Botones (activo LOW con pull-up)
#define PIN_BTN_POWER        4   // Encender/Apagar
#define PIN_BTN_PROGRAMA     16  // Seleccionar programa
#define PIN_BTN_NIVEL        17  // Seleccionar nivel de agua
#define PIN_BTN_INICIO       5   // Iniciar/Pausar ciclo

// LEDs indicadores (activo HIGH)
#define PIN_LED_PESADO       18  // LED programa pesado
#define PIN_LED_NORMAL       19  // LED programa normal
#define PIN_LED_DELICADO     21  // LED programa delicado
#define PIN_LED_RAPIDO       22  // LED programa rapido
#define PIN_LED_LAVANDO      23  // LED etapa lavado
#define PIN_LED_ENJUAGUE     13  // LED etapa enjuague
#define PIN_LED_CENTRIFUGADO 12  // LED etapa centrifugado

// ─── CONSTANTES DE SEGURIDAD ─────────────────────────────
#define TIMEOUT_LLENADO_MS   900000   // 15 minutos max para llenar
#define TIEMPO_DRENAJE_MS    90000    // 90 segundos para drenar
#define DEBOUNCE_MS          200      // Debounce de botones

// ─── ESTADOS DE LA MAQUINA DE ESTADOS ────────────────────
enum EstadoMaquina {
  APAGADA,
  IDLE,               // Encendida, esperando seleccion e inicio
  LLENADO,            // Llenando tanque
  LAVADO,             // Agitacion (lavado)
  DRENAJE_LAVADO,     // Drenando agua de lavado
  LLENADO_ENJUAGUE,   // Llenando para enjuague
  ENJUAGUE,           // Agitacion suave (enjuague)
  DRENAJE_ENJUAGUE,   // Drenando agua de enjuague
  CENTRIFUGADO,       // Centrifugado final
  FINALIZADO,         // Ciclo completado
  ERROR_TIMEOUT       // Error por timeout
};

// ─── PROGRAMAS DISPONIBLES ───────────────────────────────
enum Programa {
  PESADO = 0,
  NORMAL,
  DELICADO,
  RAPIDO,
  SOLO_CENTRIFUGADO,
  SOLO_ENJUAGUE,
  NUM_PROGRAMAS       // Contador
};

// ─── NIVELES DE AGUA ─────────────────────────────────────
enum NivelAgua {
  NIVEL_BAJO = 0,
  NIVEL_MEDIO,
  NIVEL_ALTO,
  NIVEL_EXTRA,
  NUM_NIVELES         // Contador
};

// ─── PARAMETROS DE CADA CICLO ────────────────────────────
// Tiempos calibrados segun la maquina original.
// IMPORTANTE: Ajustar estos valores midiendo con cronometro
//             los tiempos reales de la placa original antes
//             de reemplazarla.
struct ParametrosCiclo {
  unsigned long tiempoLavado;       // Tiempo total de agitacion (ms)
  unsigned long tiempoAgitacion;    // Duracion agitacion en una direccion (ms)
  unsigned long pausaAgitacion;     // Pausa entre cambio de direccion (ms)
  int           numEnjuagues;       // Cantidad de ciclos de enjuague
  unsigned long tiempoEnjuague;     // Duracion de cada enjuague (ms)
  unsigned long tiempoCentrifugado; // Duracion centrifugado final (ms)
  bool          agitacionFuerte;    // true=rapida/fuerte, false=suave
};

// Tabla de ciclos - AJUSTAR SEGUN MEDICIONES REALES
const ParametrosCiclo ciclos[NUM_PROGRAMAS] = {
  // PESADO:  lavado 15min, agit 4s/dir, pausa 2s, 2 enjuagues 4min, centrif 7min
  { 900000, 4000, 2000, 2, 240000, 420000, true },
  // NORMAL:  lavado 12min, agit 4s/dir, pausa 2s, 2 enjuagues 3min, centrif 5min
  { 720000, 4000, 2000, 2, 180000, 300000, true },
  // DELICADO: lavado 7min, agit 3s/dir, pausa 4s, 1 enjuague 3min, centrif 3min
  { 420000, 3000, 4000, 1, 180000, 180000, false },
  // RAPIDO:  lavado 5min, agit 3s/dir, pausa 2s, 1 enjuague 2min, centrif 3min
  { 300000, 3000, 2000, 1, 120000, 180000, true },
  // SOLO_CENTRIFUGADO: sin lavado, sin enjuague, centrif 7min
  { 0, 0, 0, 0, 0, 420000, true },
  // SOLO_ENJUAGUE: sin lavado, 2 enjuagues 3min, centrif 3min
  { 0, 0, 0, 2, 180000, 180000, true },
};

// ─── VARIABLES GLOBALES ──────────────────────────────────
EstadoMaquina estadoActual = APAGADA;
Programa programaSeleccionado = NORMAL;
NivelAgua nivelSeleccionado = NIVEL_MEDIO;
int enjuagueActual = 0;
unsigned long tiempoInicioEtapa = 0;
bool direccionMotor = false;
unsigned long ultimoCambioDir = 0;
unsigned long ultimoDebounce = 0;

// ─── FUNCIONES DE ACTUADORES ─────────────────────────────

void apagarTodo() {
  digitalWrite(PIN_VALVULA_AGUA, LOW);
  digitalWrite(PIN_MOTOR_DIR_A, LOW);
  digitalWrite(PIN_MOTOR_DIR_B, LOW);
  digitalWrite(PIN_CENTRIFUGADO, LOW);
  digitalWrite(PIN_BOMBA_DRENAJE, LOW);
}

void abrirAgua() {
  digitalWrite(PIN_VALVULA_AGUA, HIGH);
}

void cerrarAgua() {
  digitalWrite(PIN_VALVULA_AGUA, LOW);
}

void agitar(bool direccion) {
  if (direccion) {
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

void iniciarCentrifugado() {
  digitalWrite(PIN_CENTRIFUGADO, HIGH);
}

void pararCentrifugado() {
  digitalWrite(PIN_CENTRIFUGADO, LOW);
}

void iniciarDrenaje() {
  digitalWrite(PIN_BOMBA_DRENAJE, HIGH);
}

void pararDrenaje() {
  digitalWrite(PIN_BOMBA_DRENAJE, LOW);
}

void travarTapa() {
  digitalWrite(PIN_TRAVA_TAPA, HIGH);
}

void destravarTapa() {
  digitalWrite(PIN_TRAVA_TAPA, LOW);
}

// ─── FUNCIONES DE SENSORES ───────────────────────────────

bool nivelAlcanzado() {
  // El presostato se activa en LOW cuando el nivel es alcanzado
  switch (nivelSeleccionado) {
    case NIVEL_BAJO:
      return digitalRead(PIN_PRESOSTATO_BAJO) == LOW;
    case NIVEL_MEDIO:
      return digitalRead(PIN_PRESOSTATO_BAJO) == LOW;
    case NIVEL_ALTO:
      return digitalRead(PIN_PRESOSTATO_ALTO) == LOW;
    case NIVEL_EXTRA:
      return digitalRead(PIN_PRESOSTATO_ALTO) == LOW;
    default:
      return digitalRead(PIN_PRESOSTATO_BAJO) == LOW;
  }
}

bool tapaCerrada() {
  return digitalRead(PIN_TAPA_CERRADA) == LOW;  // Activo bajo
}

// ─── ACTUALIZACION DE LEDs DEL PANEL ─────────────────────

void actualizarLEDs() {
  // LEDs de programa seleccionado
  digitalWrite(PIN_LED_PESADO,   programaSeleccionado == PESADO);
  digitalWrite(PIN_LED_NORMAL,   programaSeleccionado == NORMAL);
  digitalWrite(PIN_LED_DELICADO, programaSeleccionado == DELICADO);
  digitalWrite(PIN_LED_RAPIDO,   programaSeleccionado == RAPIDO);

  // LEDs de etapa actual
  digitalWrite(PIN_LED_LAVANDO,
    estadoActual == LLENADO || estadoActual == LAVADO);
  digitalWrite(PIN_LED_ENJUAGUE,
    estadoActual == LLENADO_ENJUAGUE || estadoActual == ENJUAGUE);
  digitalWrite(PIN_LED_CENTRIFUGADO,
    estadoActual == CENTRIFUGADO);

  // Parpadeo en FINALIZADO (indicar que termino)
  if (estadoActual == FINALIZADO) {
    bool parpadeo = (millis() / 500) % 2;
    digitalWrite(PIN_LED_LAVANDO, parpadeo);
    digitalWrite(PIN_LED_ENJUAGUE, parpadeo);
    digitalWrite(PIN_LED_CENTRIFUGADO, parpadeo);
  }
}

// ─── MAQUINA DE ESTADOS PRINCIPAL ────────────────────────

void ejecutarCiclo() {
  const ParametrosCiclo &params = ciclos[programaSeleccionado];
  unsigned long tiempoEnEtapa = millis() - tiempoInicioEtapa;

  switch (estadoActual) {

    // ── LLENADO ──────────────────────────────────────────
    case LLENADO:
      abrirAgua();
      if (nivelAlcanzado()) {
        cerrarAgua();
        if (params.tiempoLavado > 0) {
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
      // Seguridad: timeout de llenado
      if (tiempoEnEtapa > TIMEOUT_LLENADO_MS) {
        cerrarAgua();
        apagarTodo();
        destravarTapa();
        estadoActual = ERROR_TIMEOUT;
        Serial.println("ERROR: Timeout de llenado!");
      }
      break;

    // ── LAVADO (AGITACION) ───────────────────────────────
    case LAVADO: {
      unsigned long cicloAgitacion = params.tiempoAgitacion + params.pausaAgitacion;

      // Alternar direccion del motor
      if (millis() - ultimoCambioDir >= cicloAgitacion) {
        direccionMotor = !direccionMotor;
        ultimoCambioDir = millis();
      }

      // Agitar o pausar segun momento del ciclo
      if (millis() - ultimoCambioDir < params.tiempoAgitacion) {
        agitar(direccionMotor);
      } else {
        pararAgitacion();  // Pausa entre cambios de direccion
      }

      // Fin del tiempo de lavado
      if (tiempoEnEtapa >= params.tiempoLavado) {
        pararAgitacion();
        iniciarDrenaje();
        estadoActual = DRENAJE_LAVADO;
        tiempoInicioEtapa = millis();
        Serial.println("Lavado completado -> Drenaje");
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
        } else {
          estadoActual = CENTRIFUGADO;
        }
        tiempoInicioEtapa = millis();
        Serial.println("Drenaje completado");
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
        Serial.printf("Enjuague %d/%d iniciado\n",
                      enjuagueActual + 1, params.numEnjuagues);
      }
      // Timeout de seguridad
      if (tiempoEnEtapa > TIMEOUT_LLENADO_MS) {
        cerrarAgua();
        apagarTodo();
        destravarTapa();
        estadoActual = ERROR_TIMEOUT;
      }
      break;

    // ── ENJUAGUE (AGITACION SUAVE) ───────────────────────
    case ENJUAGUE: {
      // Agitacion mas suave que en lavado (3s on / 3s off)
      unsigned long cicloEnjuague = 3000 + 3000;
      if (millis() - ultimoCambioDir >= cicloEnjuague) {
        direccionMotor = !direccionMotor;
        ultimoCambioDir = millis();
      }
      if (millis() - ultimoCambioDir < 3000) {
        agitar(direccionMotor);
      } else {
        pararAgitacion();
      }

      // Fin del enjuague
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
          // Mas enjuagues pendientes
          estadoActual = LLENADO_ENJUAGUE;
        } else {
          // Todos los enjuagues completados
          estadoActual = CENTRIFUGADO;
        }
        tiempoInicioEtapa = millis();
      }
      break;

    // ── CENTRIFUGADO ─────────────────────────────────────
    case CENTRIFUGADO:
      // Mantener drenaje abierto durante centrifugado
      iniciarDrenaje();
      iniciarCentrifugado();

      // Seguridad: si abren la tapa, parar inmediatamente
      if (!tapaCerrada()) {
        pararCentrifugado();
        pararDrenaje();
        Serial.println("ALERTA: Tapa abierta durante centrifugado!");
        // Esperar a que cierren la tapa para continuar
        // (no cambia de estado, se reanuda al cerrar)
        break;
      }

      if (tiempoEnEtapa >= params.tiempoCentrifugado) {
        pararCentrifugado();
        pararDrenaje();
        destravarTapa();
        estadoActual = FINALIZADO;
        Serial.println("=== CICLO FINALIZADO ===");
      }
      break;

    // ── FINALIZADO ───────────────────────────────────────
    case FINALIZADO:
      apagarTodo();
      destravarTapa();
      // Los LEDs parpadean (manejado en actualizarLEDs)
      break;

    // ── ERROR ────────────────────────────────────────────
    case ERROR_TIMEOUT:
      apagarTodo();
      destravarTapa();
      // Parpadeo rapido de todos los LEDs indica error
      {
        bool errorBlink = (millis() / 200) % 2;
        digitalWrite(PIN_LED_LAVANDO, errorBlink);
        digitalWrite(PIN_LED_ENJUAGUE, errorBlink);
        digitalWrite(PIN_LED_CENTRIFUGADO, errorBlink);
      }
      break;

    default:
      break;
  }
}

// ─── MANEJO DE BOTONES DEL PANEL ─────────────────────────

void leerBotones() {
  if (millis() - ultimoDebounce < DEBOUNCE_MS) return;

  // ── BOTON POWER ──
  if (digitalRead(PIN_BTN_POWER) == LOW) {
    ultimoDebounce = millis();
    if (estadoActual == APAGADA) {
      estadoActual = IDLE;
      programaSeleccionado = NORMAL;
      nivelSeleccionado = NIVEL_MEDIO;
      Serial.println("Encendida - Modo IDLE");
    } else {
      // Apagar: detener todo
      apagarTodo();
      destravarTapa();
      estadoActual = APAGADA;
      // Apagar todos los LEDs
      digitalWrite(PIN_LED_PESADO, LOW);
      digitalWrite(PIN_LED_NORMAL, LOW);
      digitalWrite(PIN_LED_DELICADO, LOW);
      digitalWrite(PIN_LED_RAPIDO, LOW);
      digitalWrite(PIN_LED_LAVANDO, LOW);
      digitalWrite(PIN_LED_ENJUAGUE, LOW);
      digitalWrite(PIN_LED_CENTRIFUGADO, LOW);
      Serial.println("Apagada");
    }
    return;
  }

  // Solo procesar otros botones si esta en IDLE
  if (estadoActual != IDLE) return;

  // ── BOTON PROGRAMA ──
  if (digitalRead(PIN_BTN_PROGRAMA) == LOW) {
    ultimoDebounce = millis();
    programaSeleccionado = (Programa)((programaSeleccionado + 1) % NUM_PROGRAMAS);
    Serial.printf("Programa: %d\n", programaSeleccionado);
  }

  // ── BOTON NIVEL DE AGUA ──
  if (digitalRead(PIN_BTN_NIVEL) == LOW) {
    ultimoDebounce = millis();
    nivelSeleccionado = (NivelAgua)((nivelSeleccionado + 1) % NUM_NIVELES);
    Serial.printf("Nivel agua: %d\n", nivelSeleccionado);
  }

  // ── BOTON INICIO ──
  if (digitalRead(PIN_BTN_INICIO) == LOW) {
    ultimoDebounce = millis();

    // Verificar tapa cerrada antes de iniciar
    if (!tapaCerrada()) {
      Serial.println("No se puede iniciar: tapa abierta!");
      // Parpadear LED como aviso
      for (int i = 0; i < 5; i++) {
        digitalWrite(PIN_LED_LAVANDO, HIGH);
        delay(100);
        digitalWrite(PIN_LED_LAVANDO, LOW);
        delay(100);
      }
      return;
    }

    // Iniciar ciclo
    travarTapa();
    enjuagueActual = 0;
    tiempoInicioEtapa = millis();
    ultimoCambioDir = millis();
    direccionMotor = false;

    const ParametrosCiclo &params = ciclos[programaSeleccionado];

    if (params.tiempoLavado > 0 || params.numEnjuagues > 0) {
      estadoActual = LLENADO;
      Serial.println("=== CICLO INICIADO: Llenado ===");
    } else {
      // Solo centrifugado: no necesita agua
      estadoActual = CENTRIFUGADO;
      Serial.println("=== CICLO INICIADO: Solo centrifugado ===");
    }
  }
}

// ─── SETUP ───────────────────────────────────────────────

void setup() {
  Serial.begin(115200);
  Serial.println("\n====================================");
  Serial.println("  Consul CWM15AB - ESP32 Controller");
  Serial.println("====================================\n");

  // Configurar pines de salida (actuadores)
  const int pinesSalida[] = {
    PIN_VALVULA_AGUA, PIN_MOTOR_DIR_A, PIN_MOTOR_DIR_B,
    PIN_CENTRIFUGADO, PIN_BOMBA_DRENAJE, PIN_TRAVA_TAPA,
    PIN_LED_PESADO, PIN_LED_NORMAL, PIN_LED_DELICADO,
    PIN_LED_RAPIDO, PIN_LED_LAVANDO, PIN_LED_ENJUAGUE,
    PIN_LED_CENTRIFUGADO
  };
  for (int pin : pinesSalida) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }

  // Configurar pines de entrada con pull-up interno
  const int pinesEntrada[] = {
    PIN_PRESOSTATO_BAJO, PIN_PRESOSTATO_ALTO,
    PIN_TAPA_CERRADA,
    PIN_BTN_POWER, PIN_BTN_PROGRAMA,
    PIN_BTN_NIVEL, PIN_BTN_INICIO
  };
  for (int pin : pinesEntrada) {
    pinMode(pin, INPUT_PULLUP);
  }

  estadoActual = APAGADA;
  Serial.println("Sistema listo. Presione POWER para encender.");
}

// ─── LOOP PRINCIPAL ──────────────────────────────────────

void loop() {
  // 1. Leer botones del panel
  leerBotones();

  // 2. Ejecutar logica del ciclo si esta activo
  if (estadoActual != APAGADA && estadoActual != IDLE) {
    ejecutarCiclo();
  }

  // 3. Actualizar LEDs del panel
  if (estadoActual != APAGADA) {
    actualizarLEDs();
  }

  // Pequena pausa para estabilidad
  delay(10);
}
