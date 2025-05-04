import NavBar from "@/components/navbar";

export default async function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <main>
      <NavBar isAuth />
      {children}
    </main>
  );
}
