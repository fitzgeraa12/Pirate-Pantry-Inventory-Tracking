import { BrowserMultiFormatOneDReader, type IScannerControls } from '@zxing/browser';
import './App.css';
import { useEffect, useRef, useState } from 'react';

function App() {
  const [scanned_code, set_scanned_code] = useState<string | null>(null);
  const video_ref = useRef<HTMLVideoElement>(null);
  const barcode_reader_controls_ref = useRef<IScannerControls>(null);
  const barcode_reader_ref = useRef<BrowserMultiFormatOneDReader>(null);

  useEffect(() => {
    const barcode_reader = new BrowserMultiFormatOneDReader();
    barcode_reader_ref.current = barcode_reader;

    barcode_reader.decodeFromVideoDevice(
      undefined,
      video_ref.current!, // Video element should be initialized by now
      (res, err) => {
        if (res) {
          set_scanned_code(res.getText());
          // barcode_reader_controls_ref.current?.stop(); // We should have the controls by now
        } if (err) {
          if (err.name !== "NotFoundException") {
            console.error(err);
          }
        }
      }
    )
      .then(controls => {
        barcode_reader_controls_ref.current = controls;
      })
      .catch(console.error);

    return () => {
      
    };
  }, []);

  return (
    <>
      <div>Scanned code: {scanned_code ? scanned_code : "NONE"}</div>
      <video ref={video_ref} style={{ width: '100%' }} />
    </>
  );
}

export default App;
