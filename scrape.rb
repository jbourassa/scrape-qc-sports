require 'nokogiri'
require 'open-uri'
require 'CGI'
require 'net/http'
require 'JSON'

def getPosition(address)
  encodedAddress = CGI::escape(address + ', Quebec, QC')
  url = "http://maps.googleapis.com/maps/api/geocode/json?address=#{encodedAddress}&sensor=false"
  puts url
  response = Net::HTTP.get URI.parse(url)
  data = JSON.parse(response)
  location = data["results"][0]['geometry']['location']
  [location['lat'], location['lng']]
end

def cleanAddress(endroit)
  addressTags = endroit
  addressTags = addressTags.next while addressTags.name.downcase != 'td'
  addressTags.xpath("span[@class='note']").unlink
  address = addressTags.content.gsub(/[\r\n\t]/, ' ').squeeze(' ').strip
  telIndex = address.index('Tél')
  unless telIndex.nil?
    address = address[0,telIndex].strip
  end

  address << ', Quebec, qc'
end

def getTerrains
  loisirs = {
    :glissoires => 'http://www.ville.quebec.qc.ca/citoyens/loisirs_sports/glissoires.aspx',
    :parcs => 'http://www.ville.quebec.qc.ca/citoyens/loisirs_sports/parcs_intergenerationnels.aspx',
    :patinoires => 'http://www.ville.quebec.qc.ca/citoyens/loisirs_sports/patinoires_interieures.aspx',
    :piscines => 'http://www.ville.quebec.qc.ca/citoyens/loisirs_sports/piscines_interieures.aspx',
    :raquettes => 'http://www.ville.quebec.qc.ca/citoyens/loisirs_sports/raquettes_ski.aspx'
  }

  terrains = []

  loisirs.keys.each do |loisir|
    doc = Nokogiri::HTML(open(loisirs[loisir]))
    endroits = doc.xpath('//th[substring(@headers, 1, 7)="endroit"]')
    endroits.each do |endroit| 
      name = endroit.content.gsub(/[\r\n\t]/, ' ').squeeze(' ').strip 
      address = cleanAddress(endroit)
      lat, lng = getPosition address
      terrains.push({ :loisir => loisir, :name => name, :address => address, :lat => lat, :lng => lng })
    end
  end

  terrains
end

puts getTerrains.to_json
