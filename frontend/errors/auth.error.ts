// import { AuthError } from "next-auth";

// export class CredentialsError extends AuthError {
//     constructor(public message: string = "Invalid credentials") {
//         super(message);
//         this.name = 'CredentialsError';
//         this.type = "CredentialsSignin";
//         this.message = message;
//     }
// }

// export class EmailVerificationError extends AuthError {
//     constructor(public message: string = "Email is not not verified") {
//         super(message);
//         this.name = 'Verification';
//         this.type = "Verification";
//         this.message = message;
//     }
// }

// export class ActiveAccountError extends AuthError {
//     constructor(public message: string = "Account is suspended, Please contact your institution") {
//         super(message);
//         this.name = 'ActiveAccountError';
//         this.type = "AccessDenied";
//         this.message = message;
//     }
// }