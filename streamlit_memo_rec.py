import streamlit as st
import pandas as pd
import time
import random
import numpy as np
import requests
import json
import base64
from io import StringIO


from st_audiorec import st_audiorec

import io
import os
from pydub import AudioSegment
import speech_recognition as sr
from io import BytesIO



# Funzione per decodificare l'audio da base64
def decode_audio(base64_audio):
    audio_bytes = base64.b64decode(base64_audio)
    return BytesIO(audio_bytes)

# Funzione per trascrivere l'audio
def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="it-IT")
            return text
        except sr.UnknownValueError:
            return "Non è stato possibile comprendere l'audio."
        except sr.RequestError as e:
            return f"Errore nel servizio di riconoscimento vocale: {e}"









def save_and_upload_to_github(data):
    # Input per i dati da salvare
    columns = ["Eta", "Gender", "Nazionalita", "Educazione", "Occupazione", "BDI2", "RRS", "PCL-5-reexperiencing", "PCL-5-avoidance", "PCL-5-altereted_cognition", "PCL-5-hyperarousal", "PCL-5-tot", "Cue-Word", "Text", "Time"]
    new_df = pd.DataFrame(data, columns=columns)
    file_name = "dati.csv"

    # Input per GitHub
    repo_name = "SanEnzoLor/memo_rec"
    branch_name = "main"
    token = st.secrets["token"]
        
    # Verifica se il file esiste nella repository
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:  # Il file esiste già
        sha = response.json()["sha"]
        content = response.json()
        # Decodifica e carica i dati esistenti
        existing_data = base64.b64decode(content["content"]).decode("utf-8")
        existing_df = pd.read_csv(StringIO(existing_data))
    else:
        sha = None  # Il file non esiste ancora
        existing_df = pd.DataFrame()  # DataFrame vuoto

    # Combina i dati esistenti con i nuovi dati
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)

    # Salva il nuovo DataFrame in CSV
    combined_csv = combined_df.to_csv(index=False)

    # Codifica il contenuto aggiornato in Base64
    content = base64.b64encode(combined_csv.encode("utf-8")).decode("utf-8")
    
    # Creazione del payload per l'API di GitHub
    payload = {
        "message": "Aggiunta file CSV tramite Streamlit",
        "content": content,
        "branch": branch_name,
    }
    if sha:  # Se il file esiste, aggiungi "sha" al payload
        payload["sha"] = sha
    
    # Richiesta POST a GitHub
    response = requests.put(url, headers=headers, data=json.dumps(payload))
            
    if response.status_code == 200:  # 200 = aggiornato
        st.success("File aggiornato con successo su GitHub!")
    elif response.status_code == 201:  # 201 = creato
        st.success("File creato con successo su GitHub!")
    else:
        st.error(f"Errore durante l'upload: {response.status_code}\n{response.json()}")
        
    st.write(new_df)
    

# Funzione per somministrare il BDI2
def BDI2():
    st.title("**Beck Depression Inventory - II**")
    st.write("Il presente questionario consiste di 21 gruppi di affermazioni.  Per ogni gruppo scelga quella che meglio descrive come si è sentito nelle ultime due settimane (incluso oggi). Se più di una affermazione dello stesso gruppo descrive ugualmente bene come si sente, faccia una crocetta sul numero più elevato per quel gruppo. Non si soffermi troppo su ogni affermazione: la prima risposta è spesso la più accurata.")
    st.markdown("https://www.endowiki.it/images/stories/pdf/Beck-II-Italiano.pdf")
    st.markdown("https://psicologiaecomunicazione.it/wp-content/uploads/2018/07/Inventario-per-la-Depressione-Di-Beck-Beck-Depression-Inventory.pdf")
    st.markdown("https://www.itsalute.com/Condizioni-Trattamenti/depressione/Come-interpretare-il-Beck-Depression-Inventory-.html")
    
    options = ["0. Non mi sento triste.", "1. Mi sento triste per la maggior parte del tempo.", "2. Mi sento sempre triste.", "3. Mi sento così triste o infelice da non poterlo sopportare."]
    items= options.index(st.selectbox("Tristezza", options))

    options = ["0. Non sono scoraggiato riguardo al mio futuro.", "1. Mi sento più scoraggiato riguardo al mio futuro rispetto al solito.", "2. Non mi aspetto nulla di buono per me.", "3. Sento che il mio futuro è senza speranza e che continuerà a peggiorare."]
    items = items + options.index(st.selectbox("Pessimismo", options))
    
    options = ["0. Non mi sento un fallito.", "1. Ho fallito più di quanto avrei dovuto.", "2. Se ripenso alla mia vita riesco a vedere solo una serie di fallimenti.", "3. Ho la sensazione di essere un fallimento totale come persona."]
    items = items + options.index(st.selectbox("Fallimento", options))

    options = ["0. Traggo lo stesso piacere di sempre dalle cose che faccio.", "1. Non traggo più piacere dalle cose come un tempo.", "2. Traggo molto poco piacere dalle cose che di solito mi divertivano.", "3. Non riesco a trarre alcun piacere dalle cose che una volta mi piacevano."]
    items = items + options.index(st.selectbox("Perdita di piacere", options))

    options = ["0. Non mi sento particolarmente in colpa.", "1. Mi sento in colpa per molte cose che ho fatto o che avrei dovuto fare.", "2. Mi sento molto spesso in colpa.", "3. Mi sento sempre in colpa."]
    items = items + options.index(st.selectbox("Senso di colpa", options))

    options = ["0. Non mi sento come se stessi subendo una punizione. ","1. Sento che potrei essere punito. ","2. Mi aspetto di essere punito. ","3. Mi sento come se stessi subendo una punizione."]
    items = items + options.index(st.selectbox("Sentimenti di punizione", options))

    options = ["0. Considero me stesso come ho sempre fatto.","1. Credo meno in me stesso.","2. Sono deluso di me stesso. ","3. Mi detesto."]
    items = items + options.index(st.selectbox("Autostima", options))

    options = ["0. Non mi critico né mi biasimo più del solito.","1. Mi critico più spesso del solito.", "2. Mi critico per tutte le mie colpe.", "3. Mi biasimo per ogni cosa brutta che mi accade."]
    items = items + options.index(st.selectbox("Autocritica", options))

    options = ["0. Non ho alcun pensiero suicida.","1. Ho pensieri suicidi ma non li realizzerei.","2. Sento che starei meglio se morissi. ","3. Se mi si presentasse l’occasione, non esiterei ad uccidermi."]
    items = items + options.index(st.selectbox("Suicidio", options))

    options = ["0. Non piango più del solito.","1. Piango più del solito. ","2. Piango per ogni minima cosa. ","3. Ho spesso voglia di piangere ma non ci riesco."]
    items = items + options.index(st.selectbox("Pianto", options))

    options = ["0. Non mi sento più agitato o teso del solito.","1. Mi sento più agitato o teso del solito. ","2. Sono così nervoso o agitato al punto che mi è difficile rimanere fermo. ","3. Sono così nervoso o agitato che devo continuare a muovermi o fare qualcosa."]
    items = items + options.index(st.selectbox("Agitazione", options))

    options = ["0. Non ho perso interesse verso le altre persone o verso le attività.", "1. Sono meno interessato agli altri o alle cose rispetto a prima. ","2. Ho perso la maggior parte dell’interesse verso le altre persone o cose. ","3. Mi risulta difficile interessarmi a qualsiasi cosa."]
    items = items + options.index(st.selectbox("Perdita di interessi", options))

    options = ["0. Prendo decisioni come sempre. ","1. Trovo più difficoltà del solito nel prendere decisioni. ","2. Ho molte più difficoltà nel prendere decisioni rispetto al solito. ","3. Non riesco a prendere nessuna decisione."]
    items = items + options.index(st.selectbox("Indecisione", options))

    options = ["0. Non mi sento inutile. ","1. Non mi sento valido e utile come un tempo. ","2. Mi sento più inutile delle altre persone. ","3. Mi sento completamente inutile su qualsiasi cosa."]
    items = items + options.index(st.selectbox("Senso di inutilità", options))

    options = ["0. Ho la stessa energia di sempre. ","1. Ho meno energia del solito. ","2. Non ho energia sufficiente per fare la maggior parte delle cose.","3. Ho così poca energia che non riesco a fare nulla."]
    items = items + options.index(st.selectbox("Perdita di energia ", options))

    options = ["0. Non ho notato alcun cambiamento nel mio modo di dormire. ", "1a. Dormo un po’ più del solito. ","1b. Dormo un po’ meno del solito. ","2a. Dormo molto più del solito. ","2b. Dormo molto meno del solito. ","3a. Dormo quasi tutto il giorno. ","3b. Mi sveglio 1-2 ore prima e non riesco a riaddormentarmi."]
    items = items + np.round(options.index(st.selectbox("Sonno", options))/2 + 0.01)

    options = ["0. Non sono più irritabile del solito. ","1. Sono più irritabile del solito. ","2. Sono molto più irritabile del solito.","3. Sono sempre irritabile."]
    items = items + options.index(st.selectbox("Irritabilità", options))

    options = ["0. Non ho notato alcun cambiamento nel mio appetito.", "1a. Il mio appetito è un po’ diminuito rispetto al solito. ","1b. Il mio appetito è un po’ aumentato rispetto al solito. ","2a. Il mi appetito è molto diminuito rispetto al solito. ","2b. Il mio appetito è molto aumentato rispetto al solito. ","3a. Non ho per niente appetito. ","3b. Mangerei in qualsiasi momento"]
    items = items + np.round(options.index(st.selectbox("Appetito", options))/2 + 0.01)

    options = ["0. Riesco a concentrarmi come sempre.","1. Non riesco a concentrarmi come al solito.","2. Trovo difficile concentrarmi per molto tempo.","3. Non riesco a concentrarmi su nulla."]
    items = items + options.index(st.selectbox("Concentrazione", options))

    options = ["0. Non sono più stanco o affaticato del solito. ","1. Mi stanco e mi affatico più facilmente del solito. ","2. Sono così stanco e affaticato che non riesco a fare molte delle cose che facevo prima. ","3. Sono talmente stanco e affaticato che non riesco più a fare nessuna delle cose che facevo prima."]
    items = items + options.index(st.selectbox("Fatica", options))

    options = ["0. Non ho notato alcun cambiamento recente nel mio interesse verso il sesso.", "1. Sono meno interessato al sesso rispetto a prima.","2. Ora sono molto meno interessato al sesso. ","3. Ho completamente perso l’interesse verso il sesso."]
    items = items + options.index(st.selectbox("Sesso", options))

    return items

# Funzione per somministrare il RRS
def RRS():
    st.title("**Ruminative Response Scale**")
    st.write("Gli individui pensano e agiscono in molti modi diversi quando si sentono depressi. Per favore, legga ciascuno dei seguenti item e indichi se, quando si sente giù, triste o depresso, lo pensa o lo fa mai, a volte, spesso o sempre. Indichi cortesemente cosa fa di solito, non cosa pensa di dover fare, selezionando il numero per indicare quanto ogni problema la affligge (da: Quasi mai = 1; a: Quasi sempre = 4)..")
    st.markdown("https://academy.formazionecontinuainpsicologia.it/wp-content/uploads/2023/07/ruminative.pdf")
    st.markdown("https://doi.org/10.1016/j.jbtep.2006.03.002")
    st.markdown("https://psychologyroots.com/ruminative-responses-scale/")
    items = st.slider("Pensare a quanto ti senti solo", min_value=1, max_value=4, step=1)
    items = items + st.slider("2. Pensare “Non sarò in grado di fare il mio lavoro perché mi sento così male”", min_value=1, max_value=4, step=1)
    items = items + st.slider("3. Pensare alle tue sensazioni di fatica e malessere", min_value=1, max_value=4, step=1)
    items = items + st.slider("4. Pensare a quanto è difficile concentrarsi", min_value=1, max_value=4, step=1)
    items = items + st.slider("5. Pensare a quanto ti senti passivo e demotivato", min_value=1, max_value=4, step=1)
    items = items + st.slider("6. Analizzare eventi recenti per cercare di comprendere perché sei depresso", min_value=1, max_value=4, step=1)
    items = items + st.slider("7. Pensare alla sensazione di non provare più niente", min_value=1, max_value=4, step=1)
    items = items + st.slider("8. Pensare “Perché non riesco a riprendermi?”", min_value=1, max_value=4, step=1)
    items = items + st.slider("9. Pensare “Perché reagisco sempre in questo modo?”", min_value=1, max_value=4, step=1)
    items = items + st.slider("10. Isolarti e pensare perché ti senti in questo modo", min_value=1, max_value=4, step=1)
    items = items + st.slider("11.Scrivere cosa pensi e analizzarlo", min_value=1, max_value=4, step=1)
    items = items + st.slider("12.Pensare a una situazione recente e desiderare che fosse andata meglio", min_value=1, max_value=4, step=1)
    items = items + st.slider("13.Pensare “Perché ho problemi che gli altri non hanno?”", min_value=1, max_value=4, step=1)
    items = items + st.slider("14.Pensare a quanto ti senti triste", min_value=1, max_value=4, step=1)
    items = items + st.slider("15.Pensare a tutte le tue mancanze, fallimenti, colpe, errori", min_value=1, max_value=4, step=1)
    items = items + st.slider("16.Pensare a quanto non hai voglia di fare nulla", min_value=1, max_value=4, step=1)
    items = items + st.slider("17.Analizzare la tua personalità per cercare di capire perché sei depresso", min_value=1, max_value=4, step=1)
    items = items + st.slider("18.Andare in giro da solo e pensare ai tuoi sentimenti", min_value=1, max_value=4, step=1)
    items = items + st.slider("19.Pensare a quanto sei arrabbiato con te stesso", min_value=1, max_value=4, step=1)
    items = items + st.slider("20.Ascoltare musica triste", min_value=1, max_value=4, step=1)
    items = items + st.slider("21.Isolarti e pensare alle ragioni per cui ti senti triste", min_value=1, max_value=4, step=1)
    items = items + st.slider("22.Cercare di comprendere te stesso focalizzandoti sui sentimenti depressivi", min_value=1, max_value=4, step=1)

    return items


# Funzione per il PTSD checklist 5
def PCL5():
    st.title("**Posttraumatic Stress Disorder Checklist - 5**")
    
    st.write("È mai stata esposta ai seguenti eventi: pericolo di morte, minaccia effettiva di lesioni gravi o di violenza, in una o più delle seguenti modalità:")
    st.write("1. Sperimentando in prima persona l'evento o gli eventi.")
    st.write("2. Assistendo a un evento o gli eventi verificati ad altri.")
    st.write("3. Apprendendo che l'evento è accaduto a un parente o a un amico stretto.")
    st.write("4. Sperimentando un'esposizione ripetuta a dettagli estremi di eventi non noti verificati ad altri (e.g., i primi soccorritori che raccolgono parti di corpi; gli agenti di polizia ripetutamente esposti a dettagli di abusi su minori).")
    trauma_event = st.selectbox("risposta", ["SI","NO"], index=1, label_visibility = "collapsed") # NO predefinito
    st.markdown("https://www.ptsd.va.gov/professional/articles/article-pdf/id1628840.pdf")
    st.markdown("https://www.ptsd.va.gov/professional/assessment/adult-sr/ptsd-checklist.asp")
    st.markdown("https://www.center-tbi.eu/files/approved-translations/Italian/ITALIAN_PCL_PW.pdf")
    st.markdown("https://novopsych.com.au/wp-content/uploads/2024/08/PTSD-assessment-pcl-5-results-report-scoring.pdf")

    if trauma_event == "SI":
        st.write("Qui sotto viene riportata una lista di problemi che talvolta le persone presentano in risposta a esperienze molto stressanti. Leggere ogni problema attentamente e selezionare il numero per indicare quanto ogni problema l'ha afflitta nell'ultima settimana (da: Per Niente = 0; a: Moltissimo = 4).")

        items_reexperiencing = st.slider("Ricordi ripetuti, disturbanti e indesiderati dell'esperienza stressante che ha subito?", min_value=0, max_value=4, step=1)
        items_reexperiencing = items_reexperiencing + st.slider("Sogni ricorrenti e disturbanti dell'esperienza stressante?", min_value=0, max_value=4, step=1)
        items_reexperiencing = items_reexperiencing + st.slider("Avere la sensazione o comportarsi improvvisamente come se l'esperienza stressante  si stesse verificando nuovamente (come se si rivivesse la stessa esperienza)?", min_value=0, max_value=4, step=1)
        items_reexperiencing = items_reexperiencing + st.slider("Sentirsi molto turbato/a quando qualcosa le ricorda l'esperienza stressante?", min_value=0, max_value=4, step=1)
        items_reexperiencing = items_reexperiencing + st.slider("Avere forti reazioni fisiche quando qualcosa Le ricorda l'esperienza stressante (per esempio battito del cuore accelerato, respiro affannoso, sudorazione)?", min_value=0, max_value=4, step=1)

        items_avoidance = st.slider("Evitare ricordi, pensieri o sensazioni legati all'esperienza stressante?", min_value=0, max_value=4, step=1)
        items_avoidance = items_avoidance + st.slider("Evitare qualunque cosa Le ricordi l'esperienza stressante (per esempio, persone, luoghi, conversazioni, attività, oggetti o situazioni)?", min_value=0, max_value=4, step=1)

        items_altereted_cognition = st.slider("Problemi a ricordare elementi importanti dell'esperienza stressante?", min_value=0, max_value=4, step=1)
        items_altereted_cognition = items_altereted_cognition + st.slider("Avere opinioni fortemente negative di sé, di altre persone o del mondo (per esempio, avere pensieri del tipo: Io sono una cattiva persona, c'è realmente qualcosa che non va in me, non ci si può fidare di nessuno, il mondo intero è pericoloso)?", min_value=0, max_value=4, step=1)
        items_altereted_cognition = items_altereted_cognition + st.slider("Incolpare se stesso/a o altre persone dell'esperienza stressante o di ciò che è accaduto in seguito?", min_value=0, max_value=4, step=1)
        items_altereted_cognition = items_altereted_cognition + st.slider("Avere sentimenti fortemente negativi come paura, terrore, rabbia, senso di colpa o vergogna?", min_value=0, max_value=4, step=1)
        items_altereted_cognition = items_altereted_cognition + st.slider("Perdita di interesse alle attività che solitamente Le piacevano?", min_value=0, max_value=4, step=1)
        items_altereted_cognition = items_altereted_cognition + st.slider("Sentirsi distante o isolato/a dal prossimo?", min_value=0, max_value=4, step=1)
        items_altereted_cognition = items_altereted_cognition + st.slider("Avere difficoltà a provare sentimenti positivi (per esempio, sentirsi incapace di provare felicità o sentimenti di affetto nei confronti di persone a Lei care)?", min_value=0, max_value=4, step=1)
        
        items_hyperarousal = st.slider("Avere un comportamento irritabile, accessi di rabbia, o reazioni aggressive?", min_value=0, max_value=4, step=1)
        items_hyperarousal = items_hyperarousal + st.slider("Correre troppi rischi o fare cose che potrebbero causarLe danno?", min_value=0, max_value=4, step=1)
        items_hyperarousal = items_hyperarousal + st.slider("Essere ipervigile, guardingo/a o sempre all'erta?", min_value=0, max_value=4, step=1)
        items_hyperarousal = items_hyperarousal + st.slider("Sentirsi in tensione o spaventarsi facilmente?", min_value=0, max_value=4, step=1)
        items_hyperarousal = items_hyperarousal + st.slider("Avere difficoltà di concentrazione?", min_value=0, max_value=4, step=1)
        items_hyperarousal = items_hyperarousal + st.slider("Avere difficoltà ad addormentarsi o a dormire?", min_value=0, max_value=4, step=1)

        tot = items_reexperiencing + items_avoidance + items_altereted_cognition + items_hyperarousal
    
    else:
        items_reexperiencing = 0
        items_avoidance = 0
        items_altereted_cognition = 0
        items_hyperarousal = 0
        tot = 0

    return items_reexperiencing, items_avoidance, items_altereted_cognition, items_hyperarousal, tot


# Interfaccia Streamlit
def main():   
    # Crea due colonne per le immagini
    col1, col2 = st.columns([0.81, 1])
    # Mostra le immagini nelle colonne
    with col1:
        st.image("image/logo_unige.png", use_container_width=True)
    with col2:
        st.image("image/logo_nextage.png", use_container_width=True)
    
    st.title("**Indici Demografici**")

    if "change" not in st.session_state:
        st.session_state.change = False
    def gend_sel():
        st.session_state.change = True
    # Creazione di input per acquisire dati dall'utente
    eta = st.number_input("Inserisci l'età:", min_value=18, max_value=80, step=1)
    gender = st.selectbox("Seleziona il genere in cui ti identifichi:", ["Maschile", "Femminile", "Non-binario", "Nessuno"], index=3, on_change = gend_sel)
    nazione = st.text_input("Scrivi la tua nazionalità:")
    educazione = st.selectbox("Seleziona il grado di istruzione più elevato conseguito:", ["Scuola primaria", "Scuola secondaria di primo grado", "Scuola secondaria di secondo grado", "Istituto tecnico superiore", "Università triennale", "Università magistrale", "Dottorato"])
    occupazione = st.selectbox("In questo momento hai un impiego:", ["SI","NO"])
    results_d = BDI2()
    st.write(f"BDI2: {results_d}")
    results_r = RRS()
    st.write(f"RRS: {results_r}")
    results_p = PCL5()
    st.write(f"PCL5: Re-experiencing = {results_p[0]}, Avoidance = {results_p[1]}, Negative alterations in cognition and mood = {results_p[2]}, Hyper-arousal = {results_p[3]}, Totale = {results_p[4]}")

    #record_seconds = 6
    st.title("**Cue-Word Autobiographic Memory Retrievial**")
    # Lista di parole spunto
    cue_words_f = ['ECCITATA', 'ANNOIATA', 'FELICE', 'FALLITA', 'FORTUNATA', 'DISPERATA', 'RILASSATA', 'SOLITARIA', 'SERENA', 'TRISTE']
    cue_words = ['ECCITATO', 'ANNOIATO', 'FELICE', 'FALLITO', 'FORTUNATO', 'DISPERATO', 'RILASSATO', 'SOLITARIO', 'SERENO', 'TRISTE']
    st.write("Il task consiste nel **ricordare e scrivere** un **evento personale** richiamato dalla **parola** che verrà mostrata una volta selezionato **Inizia**. Nel testo si descrivano quanti più **dettagli** possibili associati alla memoria autobiografica recuperarta. L'evento raccontato **NON** deve essere accaduto durante la **scorsa settimana**.")
    st.write("Terminata la scrittura sarà possibile salvare la memoria appena descritta (selezionando **Salva memoria**), il task potrà essere rieseguito per un massimo di 10 volte con parole differenti (selezionando nuovamente **Inizia** e poi **Salva memoria**). Se si desidera ci si può fermare prima (selezionando **Salva Dati**).")
    st.markdown("https://doi.org/10.1080/09658211.2018.1507042")
    st.markdown("https://pubmed.ncbi.nlm.nih.gov/15081887/")
    #st.write(f"Durata registrazione {record_seconds} secondi")

    # Gestione dello stato per i dati della sessione
    if "session_data" not in st.session_state:
        st.session_state.session_data = []  # Dati temporanei della sessione
    if "remaining_words" not in st.session_state:
        st.session_state.remaining_words = cue_words.copy()  # Parole rimanenti
    if st.session_state.change == True and gender == "Femminile":
        corrispondenti = []
        for parola1 in cue_words_f:
            # Rimuovi l'ultima lettera di parola1
            base_parola1 = parola1[:-1]
            # Controlla se esiste una parola che combacia con base_parola1
            match_trovato = any(base_parola1 == parola2[:-1] for parola2 in st.session_state.remaining_words)
            if match_trovato:
                corrispondenti.append(parola1)
        st.session_state.remaining_words = corrispondenti.copy()  # Parole rimanenti
        st.session_state.change = False
    if st.session_state.change == True and gender != "Femminile":
        corrispondenti = []
        for parola1 in cue_words:
            # Rimuovi l'ultima lettera di parola1
            base_parola1 = parola1[:-1]
            # Controlla se esiste una parola in list2 che combacia con base_parola1
            match_trovato = any(base_parola1 == parola2[:-1] for parola2 in st.session_state.remaining_words)
            if match_trovato:
                corrispondenti.append(parola1)
        st.session_state.remaining_words = corrispondenti.copy()  # Parole rimanenti
        st.session_state.change = False
    if "selected_word" not in st.session_state:
        st.session_state.selected_word = ""
    if "start_time" not in st.session_state:
        st.session_state.start_time = 0
    if "start" not in st.session_state:
        st.session_state.start = False
    if "show" not in st.session_state:
        st.session_state.show = False

    ten_w = False

    def on_button_i_click():
        st.session_state.start = True
        st.session_state.show = True
    
    # Bottone per avviare la registrazione
    if st.button("Inizia", disabled = st.session_state.start, on_click = on_button_i_click):
        if len(st.session_state.remaining_words) != 0:
            st.warning("Per il salvataggio della memoria fornita selezionare **Salva memoria**.")
            # Timer e il campo di input
            st.session_state.start_time = time.time()
            # Seleziona una parola casuale dalla lista di parole rimanenti
            st.session_state.selected_word = random.choice(st.session_state.remaining_words)
        else:
            # Se non ci sono parole da suggerire, disabilita il pulsante di registrazione
            st.warning("Hai già usato tutte le 10 parole, non è più possibile fare altre registrazioni. Selezionare **Salva Dati**")
            ten_w = True
    
    if st.session_state.show == True and ten_w == False:
        # Mostra la parola spunto
        st.write("Racconta una memoria che recuperi prendendo spunto dalla parola:")
        st.write(f"**{st.session_state.selected_word}**")

    visible = lambda x: "collapsed" if x else "visible"
    able = lambda x, y: False if x and not y else True
    testo = st.text_area("Scrivi qui il tuo testo una volta cliccato su **Inizia** e aver visto la **parola** da cui recuperare la memoria:", height = 300, key = len(st.session_state.remaining_words), disabled = able(st.session_state.show, ten_w), label_visibility = visible(st.session_state.show))
    
    def on_button_s_click():
        st.session_state.show = False
        st.session_state.start = False
    
    if len(st.session_state.remaining_words) != 0:
        if st.button("Salva memoria", disabled = not st.session_state.show, on_click = on_button_s_click):
            duration = time.time() - st.session_state.start_time
            # Aggiungi i dati di questa registrazione alla sessione
            st.session_state.session_data.append({
                "Eta": eta,
                "Gender": gender,
                "Nazionalita": nazione,
                "Educazione": educazione,
                "Occupazione": occupazione,
                "BDI2": results_d,
                "RRS" : results_r,
                "PCL-5-reexperiencing": results_p[0], 
                "PCL-5-avoidance": results_p[1],
                "PCL-5-altereted_cognition": results_p[2],
                "PCL-5-hyperarousal": results_p[3],
                "PCL-5-tot": results_p[4],
                "Cue-Word": st.session_state.selected_word,
                "Text": testo,
                "Time": duration
            })

            # Rimuovi la parola utilizzata dalla lista
            st.session_state.remaining_words.remove(st.session_state.selected_word)
            st.success(f"Registrazione completata. Dati salvati temporaneamente.")
            

    # Bottone per salvare i dati
    if st.session_state.session_data:
        if st.button(label = "Salva Dati"):
            save_and_upload_to_github(st.session_state.session_data)
            st.success("Grazie per aver partecipato al task.")
            st.session_state.session_data.clear()

    





    
    
    wav_audio_data = st_audiorec()
    if wav_audio_data is not None:
        transcribe_audio(st.audio(wav_audio_data, format='audio/wav'))





    
    

            
if __name__ == "__main__":
    main()
