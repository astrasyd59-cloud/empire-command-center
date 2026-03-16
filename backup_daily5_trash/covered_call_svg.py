import json

# Load data
with open('/home/astra/.openclaw/workspace/daily5/data_results.json', 'r') as f:
    data = json.load(f)

cvx_price = data['stocks']['CVX']['price']
strike = round(cvx_price * 1.05, 2)  # 5% OTM call
premium = 3.50  # Estimated premium

# Generate SVG for covered call payoff diagram
svg = f'''\x3csvg viewBox="0 0 600 320" class="payoff-svg" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="600" height="320" fill="#181d23"/>
  
  <!-- Grid lines -->
  <g stroke="rgba(255,255,255,0.05)" stroke-width="1">
    <line x1="50" y1="40" x2="550" y2="40"/>
    <line x1="50" y1="80" x2="550" y2="80"/>
    <line x1="50" y1="120" x2="550" y2="120"/>
    <line x1="50" y1="160" x2="550" y2="160"/>
    <line x1="50" y1="200" x2="550" y2="200"/>
    <line x1="50" y1="240" x2="550" y2="240"/>
    <line x1="50" y1="280" x2="550" y2="280"/>
    <line x1="100" y1="40" x2="100" y2="280"/>
    <line x1="200" y1="40" x2="200" y2="280"/>
    <line x1="300" y1="40" x2="300" y2="280"/>
    <line x1="400" y1="40" x2="400" y2="280"/>
    <line x1="500" y1="40" x2="500" y2="280"/>
  </g>
  
  <!-- Axes -->
  <line x1="50" y1="160" x2="550" y2="160" stroke="rgba(255,255,255,0.3)" stroke-width="1.5"/>
  <line x1="300" y1="40" x2="300" y2="280" stroke="rgba(255,255,255,0.3)" stroke-width="1.5"/>
  
  <!-- Axis labels -->
  <text x="300" y="305" text-anchor="middle" fill="rgba(232,230,224,0.5)" font-family="IBM Plex Mono" font-size="10">Stock Price at Expiration ($)</text>
  <text x="20" y="165" text-anchor="middle" fill="rgba(232,230,224,0.5)" font-family="IBM Plex Mono" font-size="10" transform="rotate(-90 20 165)">Profit/Loss ($)</text>
  
  <!-- Price markers -->
  <text x="100" y="295" text-anchor="middle" fill="rgba(232,230,224,0.4)" font-family="IBM Plex Mono" font-size="9">170</text>
  <text x="200" y="295" text-anchor="middle" fill="rgba(232,230,224,0.4)" font-family="IBM Plex Mono" font-size="9">180</text>
  <text x="300" y="295" text-anchor="middle" fill="#c9a84c" font-family="IBM Plex Mono" font-size="10" font-weight="600">{cvx_price:.0f} (Current)</text>
  <text x="400" y="295" text-anchor="middle" fill="#a78bfa" font-family="IBM Plex Mono" font-size="10" font-weight="600">{strike:.0f} (Strike)</text>
  <text x="500" y="295" text-anchor="middle" fill="rgba(232,230,224,0.4)" font-family="IBM Plex Mono" font-size="9">210</text>
  
  <!-- P/L markers -->
  <text x="42" y="85" text-anchor="end" fill="#4caf82" font-family="IBM Plex Mono" font-size="9">+$500</text>
  <text x="42" y="125" text-anchor="end" fill="rgba(232,230,224,0.4)" font-family="IBM Plex Mono" font-size="9">+$250</text>
  <text x="42" y="165" text-anchor="end" fill="rgba(232,230,224,0.4)" font-family="IBM Plex Mono" font-size="9">$0</text>
  <text x="42" y="245" text-anchor="end" fill="#e05555" font-family="IBM Plex Mono" font-size="9">-$500</text>
  
  <!-- Breakeven line -->
  <line x1="280" y1="40" x2="280" y2="280" stroke="#f59e42" stroke-width="1" stroke-dasharray="4,4"/>
  <text x="275" y="55" text-anchor="end" fill="#f59e42" font-family="IBM Plex Mono" font-size="9">Breakeven: ${cvx_price - premium:.2f}</text>
  
  <!-- Strike line -->
  <line x1="400" y1="40" x2="400" y2="280" stroke="#a78bfa" stroke-width="1" stroke-dasharray="4,4"/>
  
  <!-- Covered Call Payoff Line -->
  <polyline points="50,240 100,220 150,200 200,180 250,160 280,140 300,120 350,100 400,80 450,80 500,80 550,80" 
    fill="none" stroke="#4caf82" stroke-width="2.5"/>
  
  <!-- Capped profit zone -->
  <rect x="400" y="40" width="150" height="45" fill="rgba(167,139,250,0.1)"/>
  <text x="475" y="70" text-anchor="middle" fill="#a78bfa" font-family="IBM Plex Mono" font-size="9">Max Profit Zone</text>
  
  <!-- Legend -->
  <g transform="translate(360, 20)">
    <line x1="0" y1="0" x2="20" y2="0" stroke="#4caf82" stroke-width="2"/>
    <text x="26" y="4" fill="rgba(232,230,224,0.6)" font-family="IBM Plex Mono" font-size="9">Covered Call P/L</text>
  </g>
  
  <!-- Annotation -->
  <text x="50" y="25" fill="rgba(232,230,224,0.7)" font-family="IBM Plex Mono" font-size="10">CVX Covered Call: Buy 100 shares @ ${cvx_price:.2f}, Sell {strike:.0f} Call @ ${premium:.2f}</text>
</svg>'''

with open('/home/astra/.openclaw/workspace/daily5/covered_call.svg', 'w') as f:
    f.write(svg)

print("✅ Covered Call payoff SVG created for CVX")
print(f"   - Current price: ${cvx_price:.2f}")
print(f"   - Strike price: ${strike:.2f}")
print(f"   - Premium: ${premium:.2f}")
