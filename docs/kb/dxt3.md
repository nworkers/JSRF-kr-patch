# DXT3 (BC2) 텍스처 압축

* DXT3은 S3TC 블록 압축의 하나로, Direct3D 10 이후 이름은 BC2다. 4×4 픽셀 블록 하나가 16바이트다: 앞 8바이트는 픽셀마다 4비트 alpha(줄마다 `u16` 하나, 낮은 비트가 왼쪽), 뒤 8바이트는 DXT1과 같은 색 블록(RGB565 두 색 + 픽셀마다 2비트 인덱스). 그래서 1픽셀이 1바이트다. 출처: [Microsoft, Block compression, BC2](https://learn.microsoft.com/en-us/windows/win32/direct3d10/d3d10-graphics-programming-guide-resources-block-compression#bc2), [Khronos Data Format Specification, S3TC](https://registry.khronos.org/DataFormat/specs/1.3/dataformat.1.3.html#s3tc).
* Xbox에서 압축 텍스처는 스위즐하지 않고 블록을 선형 순서로 둔다(**추정**, `jetfont.dat`를 선형으로 읽어 글자가 바르게 나온 것과 일치).
* `jetfont.dat`의 색 블록은 모두 흰색이고 글자 모양은 4비트 alpha(16단계)에만 있다. 새 아틀라스는 alpha만 계산하고 색 블록은 흰색으로 채우면 된다. 구조는 [analysis/text-renderer.md §3](../analysis/text-renderer.md)에 있다.

---

# DXT3 (BC2) texture compression

* DXT3 is one of the S3TC block formats, named BC2 from Direct3D 10 on. Each 4×4 pixel block takes 16 bytes: 8 bytes of 4-bit alpha per pixel (one `u16` per row, low bits on the left), then an 8-byte colour block as in DXT1 (two RGB565 colours plus a 2-bit index per pixel), so one byte per pixel. Sources: [Microsoft, Block compression, BC2](https://learn.microsoft.com/en-us/windows/win32/direct3d10/d3d10-graphics-programming-guide-resources-block-compression#bc2), [Khronos Data Format Specification, S3TC](https://registry.khronos.org/DataFormat/specs/1.3/dataformat.1.3.html#s3tc).
* On the Xbox, compressed textures are not swizzled; blocks are in linear order (**inferred**, consistent with `jetfont.dat` decoding correctly when read linearly).
* In `jetfont.dat` every colour block is white and the glyph shapes live only in the 4-bit alpha (16 levels). A new atlas only needs computed alpha with white colour blocks. The structure is in [analysis/text-renderer.md §3](../analysis/text-renderer.md).
