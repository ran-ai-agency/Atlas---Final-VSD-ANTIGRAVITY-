import { NextRequest, NextResponse } from 'next/server';
import { createToken, setSessionCookie, validateCredentials } from '@/lib/auth';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { username, password } = body;

    if (!username || !password) {
      return NextResponse.json(
        { error: 'Nom d\'utilisateur et mot de passe requis' },
        { status: 400 }
      );
    }

    // Debug: log environment variables (remove in production)
    console.log('Login attempt:', {
      username,
      envUsername: process.env.ADMIN_USERNAME,
      envPasswordSet: !!process.env.ADMIN_PASSWORD,
      envPasswordLength: process.env.ADMIN_PASSWORD?.length
    });

    if (!validateCredentials(username, password)) {
      return NextResponse.json(
        { error: 'Identifiants invalides' },
        { status: 401 }
      );
    }

    const token = await createToken(username);
    await setSessionCookie(token);

    return NextResponse.json({
      success: true,
      message: 'Connexion reussie',
    });
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { error: 'Erreur lors de la connexion' },
      { status: 500 }
    );
  }
}
