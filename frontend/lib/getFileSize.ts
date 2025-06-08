const KB_SIZE = 1024;
const MB_SIZE = KB_SIZE * 1024;
const GB_SIZE = MB_SIZE * 1024;

export function GetFileSizeFromBytes(size: number) {
  if (size < KB_SIZE) {
    return `${size} bytes`;
  } else if (size < MB_SIZE) {
    return `${(size / KB_SIZE).toFixed(2)} KB`;
  } else if (size < GB_SIZE) {
    return `${(size / MB_SIZE).toFixed(2)} MB`;
  } else {
    return `${(size / GB_SIZE).toFixed(2)} GB`;
  }
}
