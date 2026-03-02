import struct, zlib, binascii

def png_solid_rgba(width, height, rgba):
    # rgba: tuple (r,g,b,a) 0-255
    r,g,b,a = rgba
    # each scanline: filter byte 0 + pixels
    row = bytes([0]) + bytes([r,g,b,a]) * width
    raw = row * height
    comp = zlib.compress(raw, level=9)

    def chunk(typ, data):
        crc = binascii.crc32(typ + data) & 0xffffffff
        return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", crc)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # 8-bit, RGBA
    return sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', comp) + chunk(b'IEND', b'')

def ico_with_png(png_bytes, width, height):
    # ICONDIR (6 bytes) + ICONDIRENTRY (16 bytes) + image data
    reserved = 0
    typ = 1      # icon
    count = 1
    icondir = struct.pack("<HHH", reserved, typ, count)

    w = width if width < 256 else 0
    h = height if height < 256 else 0
    colorcount = 0
    reserved2 = 0
    planes = 1
    bitcount = 32
    bytesinres = len(png_bytes)
    imageoffset = 6 + 16

    entry = struct.pack(
        "<BBBBHHII",
        w, h, colorcount, reserved2,
        planes, bitcount,
        bytesinres, imageoffset
    )
    return icondir + entry + png_bytes

def main():
    # dark background close to #0b1220
    png = png_solid_rgba(64, 64, (11, 18, 32, 255))
    ico = ico_with_png(png, 64, 64)
    with open("favicon.ico", "wb") as f:
        f.write(ico)
    print("Generated favicon.ico (64x64, solid RGBA)")

if __name__ == "__main__":
    main()
