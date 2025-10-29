import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { apiClient } from './api';

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        username: { label: 'Username', type: 'text' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) {
          return null;
        }

        try {
          const authResponse = await apiClient.login({
            username: credentials.username as string,
            password: credentials.password as string,
          });

          if (authResponse) {
            // Return user with tokens
            return {
              id: authResponse.user.id.toString(),
              name: `${authResponse.user.first_name} ${authResponse.user.last_name}`,
              email: authResponse.user.email,
              accessToken: authResponse.access,
              refreshToken: authResponse.refresh,
            };
          }

          return null;
        } catch (error) {
          console.error('Login error:', error);
          return null;
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      // Initial sign in
      if (user) {
        token.accessToken = (user as any).accessToken;
        token.refreshToken = (user as any).refreshToken;
        token.id = user.id;
      }

      return token;
    },
    async session({ session, token }) {
      // Send properties to the client
      session.user.id = token.id as string;
      (session as any).accessToken = token.accessToken;
      (session as any).refreshToken = token.refreshToken;

      return session;
    },
  },
  pages: {
    signIn: '/login',
  },
  session: {
    strategy: 'jwt',
  },
});
