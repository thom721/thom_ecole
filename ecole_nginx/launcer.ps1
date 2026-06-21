Add-Type -AssemblyName PresentationFramework, WindowsBase

# --- CONFIGURATION ---
$apiUrl = "http://127.0.0.1:8000/health"
$citations = @(
    "L'éducation est le passeport pour l'avenir.",
    "Chaque enfant qu'on enseigne est un homme qu'on gagne.",
    "La connaissance est la seule chose qui s'accroît quand on la partage.",
    "Le succès est la somme de petits efforts répététés jour après jour."
)
$randomQuote = $citations | Get-Random

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
}
"@



[xml]$XAML = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Lekol360" Height="300" Width="600" WindowStyle="None" 
        AllowsTransparency="True" Background="Transparent" WindowStartupLocation="CenterScreen" Topmost="True">
    <Grid x:Name="RootGrid" Cursor="Hand">
        <Border CornerRadius="25" Background="#004A7C" Opacity="0.95">
            <Grid>
                <Button x:Name="BtnMin" Content="−" VerticalAlignment="Top" HorizontalAlignment="Right" 
                        Margin="0,15,20,0" Width="30" Height="30" Background="Transparent" 
                        Foreground="White" FontSize="20" BorderThickness="0" Cursor="Hand"/>
                
                <StackPanel VerticalAlignment="Center" HorizontalAlignment="Center">
                    <TextBlock Text="LEKOL 360" FontSize="50" Foreground="White" FontWeight="Bold" HorizontalAlignment="Center"/>
                    
                    <TextBlock x:Name="QuoteDisplay" Text="" FontSize="16" Foreground="#E0E0E0" 
                               Margin="40,10,40,20" TextAlignment="Center" Width="480" TextWrapping="Wrap" FontStyle="Italic"/>
                    
                    <ProgressBar x:Name="ProgBar" Height="10" Width="450" Minimum="0" Maximum="100" Value="0" Foreground="#007ACC" Background="#111111"/>
                    <TextBlock x:Name="StatusText" Text="Initialisation..." Foreground="White" FontSize="14" Margin="0,15,0,0" HorizontalAlignment="Center"/>
                </StackPanel>
            </Grid>
        </Border>
    </Grid>
</Window>
"@


$reader = New-Object System.Xml.XmlNodeReader $XAML
$Form = [Windows.Markup.XamlReader]::Load($reader)

$ProgBar      = $Form.FindName("ProgBar")
$StatusText   = $Form.FindName("StatusText")
$QuoteDisplay = $Form.FindName("QuoteDisplay")
$RootGrid     = $Form.FindName("RootGrid")
$BtnMin       = $Form.FindName("BtnMin")

# --- CORRECTION 1 : AFFICHER LA PREMIÈRE CITATION TOUT DE SUITE ---
$QuoteDisplay.Text = $citations | Get-Random

$BtnMin.Add_Click({ $Form.WindowState = "Minimized" })

function Do-Events {
    $frame = New-Object System.Windows.Threading.DispatcherFrame
    [System.Windows.Threading.Dispatcher]::CurrentDispatcher.BeginInvoke([System.Windows.Threading.DispatcherPriority]::Background, [Action[System.Windows.Threading.DispatcherFrame]]{ param($f) $f.Continue = $false }, $frame)
    [System.Windows.Threading.Dispatcher]::PushFrame($frame)
}

function Test-Server {
    try {
        $response = Invoke-WebRequest -Uri $apiUrl -Method Get -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop
        return $response.StatusCode -eq 200
    } catch { return $false }
}

$Form.Show()

$progress = 0
$lastQuoteUpdate = Get-Date

# --- CORRECTION 2 : BOUCLE ACTIVE ---
while ($progress -lt 100) {
    if ($progress -lt 95) { $progress += 1 }

    $ProgBar.Value = $progress

    # Changer la citation toutes les 5 secondes même pendant le chargement
    if (((Get-Date) - $lastQuoteUpdate).TotalSeconds -gt 5) {
        $QuoteDisplay.Text = $citations | Get-Random
        $lastQuoteUpdate = Get-Date
    }

    if (Test-Server) { 
        $progress = 100 
        $StatusText.Text = "Prêt ! Cliquez n'importe où pour entrer dans Lekol360."
    } elseif ($progress -ge 95) {
        $StatusText.Text = "Attente du moteur Lekol360..."
    }

    if ($progress -eq 20) { $StatusText.Text = "Chargement des modules..." }
    if ($progress -eq 50) { $StatusText.Text = "Initialisation base de données..." }
    
    Do-Events
    Start-Sleep -Milliseconds 50
}

# --- LOGIQUE DE LANCEMENT AU CLIC ---
$RootGrid.Add_MouseLeftButtonDown({
   # if ($progress -ge 100) { # On ne lance que si le serveur est prêt
   if ($progress -ge 100){
        $RootGrid.IsEnabled = $false
        $StatusText.Text = "Ouverture de Lekol360..."
        Do-Events

        $process = Start-Process -FilePath "C:\Program Files\gestion ecole\app.exe" -PassThru

        # Tâche de fermeture automatique quand l'app apparaît
        [System.Threading.Tasks.Task]::Run([Action]{
            $maxWait = 100
            for ($i = 0; $i -lt $maxWait; $i++) {
                Start-Sleep -Milliseconds 200
                if ($process.MainWindowHandle -ne 0) {
                    $Form.Dispatcher.Invoke([Action]{ $Form.Close() })
                    break
                }
                $process.Refresh()
            }
        })
    }
})

# Garder la fenêtre ouverte pour attendre le clic
while ($Form.IsVisible) {
    Do-Events
    Start-Sleep -Milliseconds 100
}