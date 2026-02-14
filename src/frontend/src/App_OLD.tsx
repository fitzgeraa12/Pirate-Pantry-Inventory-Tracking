import { BrowserMultiFormatOneDReader, type IScannerControls } from '@zxing/browser';
import './App.css';
import { useEffect, useRef, useState } from 'react';

interface ProductResult  {
  product: Product,
}

interface Product {
  product_name: string,
}

function App() {
  const [scanned_id, set_scanned_id] = useState<string | null>(null);
  const video_ref = useRef<HTMLVideoElement>(null);
  const barcode_reader_controls_ref = useRef<IScannerControls>(null);
  const barcode_reader_ref = useRef<BrowserMultiFormatOneDReader>(null);
  const last_scanned_ref = useRef<string | null>(null);

  useEffect(() => {
    const barcode_reader = new BrowserMultiFormatOneDReader();
    barcode_reader_ref.current = barcode_reader;

    barcode_reader.decodeFromVideoDevice(
      undefined,
      video_ref.current!, // Video element should be initialized by now
      (res, err) => {
        if (res) {
          const id = res.getText();
          if (last_scanned_ref.current != id) {
            set_scanned_id(id);
            last_scanned_ref.current = id;
            fetch(`https://world.openfoodfacts.org/api/v2/product/${id}.json`)
              .then((usda_res: Response) => {
                  usda_res.json()
                    .then((product_res: ProductResult) => {
                      const product = product_res.product;
                      console.log(product);
                      console.log(product.product_name);
                    })
                    .catch(console.error);
              })
              .catch(console.error);
          }
        } if (err) {
          if (err.name !== "NotFoundException2") {
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
      <div>Scanned code: {scanned_id ? scanned_id : "NONE"}</div>
      <video ref={video_ref} style={{ width: '100%' }} />
    </>
  );
}

export default App;
