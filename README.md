# VortexBeamAnalysis

為了方便大量做 vortex beam analysis 將許多功能寫成 UI 方便使用者將所有 data 同時匯入處理。

### Flow
row data -> crop -> FFT -> output "FFT Image" and "FFT peak"

- row data
拿到 row data 為 OM image or SEM image。

- crop
由於為了在 FFT 上可以得到更好的對比度。

- FFT 
做 FFT 數學外，整合了 scalebar 可以做單位轉換，還有simulate_ellipse 可以人工對FFT peak 選定 peak point 擬和出適當的空間週期。

最後將 FFT peak 存放在 txt 中。
