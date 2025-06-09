const HOURS_IN_SECONDS = 3600;
const MINUTES_IN_SECONDS = 60;

export const convertSecondsToTime = (seconds: number) => {
    const hours = Math.floor(seconds / HOURS_IN_SECONDS);
    const minutes = Math.floor((seconds % HOURS_IN_SECONDS) / MINUTES_IN_SECONDS);
    const remainingSeconds = seconds % MINUTES_IN_SECONDS;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}