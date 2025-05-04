export const getNameInitials = (name: string) => {
    const nameSplitted = name.split(" ");
    if (nameSplitted.length === 1)
        return nameSplitted[0][0].toLocaleUpperCase() + nameSplitted[0][1].toLocaleUpperCase();
    return nameSplitted[0][0].toLocaleUpperCase() + nameSplitted[1][0].toLocaleUpperCase();
};