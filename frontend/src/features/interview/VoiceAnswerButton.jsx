
import { useEffect, useRef, useState } from "react";
import { Mic, MicOff } from "lucide-react";

function VoiceAnswerButton({
  onTranscript,
  disabled = false,
  language = "en-IN",
}) {
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState("");

  const recognitionRef = useRef(null);

  const startListening = () => {
    setError("");

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setError(
        "Speech recognition is not supported in this browser. Please use Chrome or Edge."
      );
      return;
    }

    try {
      const recognition = new SpeechRecognition();

      recognition.lang = language;
      recognition.continuous = true;
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event) => {
        let transcript = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            transcript += event.results[i][0].transcript + " ";
          }
        }

        if (transcript.trim()) {
          onTranscript(transcript.trim());
        }
      };

      recognition.onerror = (event) => {
        setIsListening(false);

        if (event.error === "not-allowed") {
          setError("Microphone permission denied. Please allow microphone access.");
        } else if (event.error === "no-speech") {
          setError("No speech detected. Please try speaking again.");
        } else if (event.error !== "aborted") {
          setError("Speech recognition failed. Please try again.");
        }
      };

      recognition.onend = () => {
        setIsListening(false);
        recognitionRef.current = null;
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      setIsListening(false);
      setError("Unable to start microphone. Please try again.");
      recognitionRef.current = null;
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
        recognitionRef.current = null;
      }
    };
  }, []);

  return (
    <div className="voice-answer-control">
      <button
        type="button"
        className={`voice-answer-btn ${isListening ? "recording" : ""}`}
        onClick={isListening ? stopListening : startListening}
        disabled={disabled}
      >
        {isListening ? <MicOff size={18} /> : <Mic size={18} />}

        {isListening ? "Stop Recording" : "Answer with Voice"}
      </button>

      {isListening && (
        <p className="voice-listening-status">
          Listening... Speak your answer clearly.
        </p>
      )}

      {error && (
        <p className="voice-error-message">
          {error}
        </p>
      )}
    </div>
  );
}

export default VoiceAnswerButton;
